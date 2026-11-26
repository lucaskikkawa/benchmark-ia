import math
import unittest

import fake_api
from fake_api import CONEXAO, ERRO_429, ERRO_500, ERRO_503, LENTO, OK, FakeAPI, Resposta
from cliente import ClienteAPI, ErroAPI, FalhaPermanente, NaoEncontrado


class FakePersonalizada:
    def __init__(self, resultados):
        self._resultados = list(resultados)
        self.chamadas = []

    def requisitar(self, metodo, caminho, timeout):
        self.chamadas.append((metodo, caminho, timeout))
        item = self._resultados.pop(0)
        if isinstance(item, Exception):
            raise item
        return item


class ClienteAPITest(unittest.TestCase):
    def test_validacao_init(self):
        api = FakeAPI()
        for kwargs in [
            {"max_tentativas": 0},
            {"max_tentativas": -3},
            {"max_tentativas": False},
            {"timeout": 0},
            {"timeout": -0.1},
            {"timeout": float("nan")},
            {"backoff_base": -0.1},
            {"backoff_base": float("nan")},
            {"backoff_max": -1.0},
            {"backoff_max": float("nan")},
            {"orcamento_espera": -0.01},
            {"orcamento_espera": float("nan")},
        ]:
            with self.subTest(kwargs=kwargs):
                with self.assertRaises(ValueError):
                    ClienteAPI(api, **kwargs)

        # Valores limites válidos
        c = ClienteAPI(api, max_tentativas=1, backoff_base=0, backoff_max=0, timeout=0.001, orcamento_espera=0)
        self.assertEqual(c.timeout, 0.001)

    def test_validacao_id_obter_usuario(self):
        api = FakeAPI()
        c = ClienteAPI(api, dormir=lambda _: None)
        for invalido in [0, -1, True, False, "1", 1.0, None, [1]]:
            with self.subTest(invalido=invalido):
                with self.assertRaises(ValueError):
                    c.obter_usuario(invalido)
        self.assertEqual(api.chamadas, [])

    def test_sucesso_200_e_exemplo(self):
        cliente = ClienteAPI(FakeAPI(seed=1, taxa_falha=0.4), max_tentativas=6, dormir=lambda s: None)
        self.assertEqual(cliente.obter_usuario(7), {"id": 7, "nome": "Usuario 7"})

    def test_404_imediato_sem_retry_nem_sleep(self):
        api = FakeAPI(roteiro=[OK])
        sleeps = []
        c = ClienteAPI(api, max_tentativas=4, dormir=sleeps.append)
        with self.assertRaises(NaoEncontrado) as ctx:
            c.obter_usuario(fake_api.MAX_ID + 1)
        self.assertIsInstance(ctx.exception, ErroAPI)
        self.assertEqual(ctx.exception.status, 404)
        self.assertEqual(len(api.chamadas), 1)
        self.assertEqual(sleeps, [])

    def test_status_nao_retentaveis_imediatos(self):
        for status in (301, 400, 401, 403, 405, 501):
            with self.subTest(status=status):
                api = FakePersonalizada([Resposta(status, {"erro": "x"}), Resposta(200, {"id": 1})])
                sleeps = []
                c = ClienteAPI(api, max_tentativas=4, dormir=sleeps.append)
                with self.assertRaises(ErroAPI) as ctx:
                    c.obter_usuario(1)
                self.assertNotIsInstance(ctx.exception, NaoEncontrado)
                self.assertNotIsInstance(ctx.exception, FalhaPermanente)
                self.assertEqual(ctx.exception.status, status)
                self.assertEqual(len(api.chamadas), 1)
                self.assertEqual(sleeps, [])

    def test_excecao_nao_retentavel_propaga(self):
        class ErroEstranho(Exception):
            pass

        api = FakePersonalizada([ErroEstranho("boom"), Resposta(200, {"id": 1})])
        sleeps = []
        c = ClienteAPI(api, max_tentativas=4, dormir=sleeps.append)
        with self.assertRaises(ErroEstranho):
            c.obter_usuario(1)
        self.assertEqual(len(api.chamadas), 1)
        self.assertEqual(sleeps, [])

    def test_todos_retentaveis_e_backoff(self):
        api = FakePersonalizada([
            Resposta(429),
            Resposta(500),
            Resposta(502),
            Resposta(503),
            Resposta(504),
            fake_api.ErroConexao("conn"),
            fake_api.TempoEsgotado("timeout"),
            Resposta(200, {"id": 42}),
        ])
        sleeps = []
        c = ClienteAPI(api, max_tentativas=8, backoff_base=0.5, backoff_max=8.0, timeout=1.5, dormir=sleeps.append)
        res = c.obter_usuario(42)
        self.assertEqual(res, {"id": 42})
        self.assertEqual(sleeps, [0.5, 1.0, 2.0, 4.0, 8.0, 8.0, 8.0])
        self.assertEqual(len(api.chamadas), 8)
        self.assertTrue(all(ch == ("GET", "/usuarios/42", 1.5) for ch in api.chamadas))

    def test_retry_after_valido_e_invalido_case_insensitive(self):
        api = FakePersonalizada([
            Resposta(429, headers={"retry-after": "1.5"}),
            Resposta(429, headers={"RETRY-AFTER": "20"}),
            Resposta(429, headers={"Retry-After": "-1"}),
            Resposta(429, headers={"Retry-After": "nan"}),
            Resposta(429, headers={"Retry-After": "inf"}),
            Resposta(429, headers={"Retry-After": "abc"}),
            Resposta(429, headers={}),
            Resposta(429, headers={"Retry-After": "0"}),
            Resposta(200, {"id": 1}),
        ])
        sleeps = []
        c = ClienteAPI(api, max_tentativas=10, backoff_base=0.5, backoff_max=8.0, dormir=sleeps.append)
        self.assertEqual(c.obter_usuario(1), {"id": 1})
        # n=1: Retry-After 1.5 -> 1.5
        # n=2: Retry-After 20 -> min(8.0, 20) = 8.0
        # n=3: -1 inválido -> 0.5 * 2^2 = 2.0
        # n=4: nan inválido -> 0.5 * 2^3 = 4.0
        # n=5: inf inválido -> 0.5 * 2^4 = 8.0
        # n=6: abc inválido -> min(8.0, 16.0) = 8.0
        # n=7: faltando -> 8.0
        # n=8: "0" -> 0.0
        self.assertEqual(sleeps, [1.5, 8.0, 2.0, 4.0, 8.0, 8.0, 8.0, 0.0])

    def test_max_tentativas_grande_sem_overflow(self):
        api = FakePersonalizada([Resposta(500)] * 2000)
        sleeps = []
        c = ClienteAPI(api, max_tentativas=2000, backoff_base=0.5, backoff_max=8.0, dormir=sleeps.append)
        with self.assertRaises(FalhaPermanente) as ctx:
            c.obter_usuario(1)
        self.assertEqual(ctx.exception.tentativas, 2000)
        self.assertEqual(ctx.exception.status, 500)
        self.assertIsNone(ctx.exception.__cause__)
        self.assertEqual(len(sleeps), 1999)
        self.assertEqual(sleeps[0], 0.5)
        self.assertEqual(sleeps[-1], 8.0)

    def test_encadeamento_causa_excecao_vs_http(self):
        # Última falha é exceção -> __cause__ é a exceção
        err = fake_api.TempoEsgotado("demorou")
        api1 = FakePersonalizada([Resposta(500), err])
        c1 = ClienteAPI(api1, max_tentativas=2, dormir=lambda _: None)
        with self.assertRaises(FalhaPermanente) as ctx1:
            c1.obter_usuario(1)
        self.assertEqual(ctx1.exception.tentativas, 2)
        self.assertIs(ctx1.exception.__cause__, err)

        # Primeira é exceção, última é HTTP -> __cause__ é None
        api2 = FakePersonalizada([fake_api.ErroConexao("queda"), Resposta(503)])
        c2 = ClienteAPI(api2, max_tentativas=2, dormir=lambda _: None)
        with self.assertRaises(FalhaPermanente) as ctx2:
            c2.obter_usuario(1)
        self.assertEqual(ctx2.exception.tentativas, 2)
        self.assertIsNone(ctx2.exception.__cause__)
        self.assertEqual(ctx2.exception.status, 503)

    def test_orcamento_espera(self):
        # 0.5 + 1.0 = 1.5 <= 1.5; próxima seria 2.0 -> 3.5 > 1.5 -> desiste na tentativa 3 sem dormir
        api = FakeAPI(roteiro=[ERRO_500, ERRO_503, CONEXAO, OK])
        sleeps = []
        c = ClienteAPI(api, max_tentativas=5, backoff_base=0.5, backoff_max=8.0, dormir=sleeps.append, orcamento_espera=1.5)
        with self.assertRaises(FalhaPermanente) as ctx:
            c.obter_usuario(1)
        self.assertEqual(ctx.exception.tentativas, 3)
        self.assertIsInstance(ctx.exception.__cause__, fake_api.ErroConexao)
        self.assertEqual(sleeps, [0.5, 1.0])
        self.assertEqual(len(api.chamadas), 3)

    def test_orcamento_espera_precisao_decimal(self):
        # 0.1 + 0.2 == 0.3 não deve estourar orcamento_espera=0.3
        api = FakePersonalizada([Resposta(500), Resposta(500), Resposta(200, {"id": 1})])
        sleeps = []
        c = ClienteAPI(api, max_tentativas=4, backoff_base=0.1, backoff_max=8.0, dormir=sleeps.append, orcamento_espera=0.3)
        self.assertEqual(c.obter_usuario(1), {"id": 1})
        self.assertEqual(sleeps, [0.1, 0.2])

    def test_orcamento_zero(self):
        api = FakeAPI(roteiro=[LENTO, OK])
        sleeps = []
        c = ClienteAPI(api, max_tentativas=4, backoff_base=0.5, timeout=1.0, dormir=sleeps.append, orcamento_espera=0.0)
        with self.assertRaises(FalhaPermanente) as ctx:
            c.obter_usuario(1)
        self.assertEqual(ctx.exception.tentativas, 1)
        self.assertIsInstance(ctx.exception.__cause__, fake_api.TempoEsgotado)
        self.assertEqual(sleeps, [])

    def test_obter_varios(self):
        api = FakeAPI(roteiro=[ERRO_429, OK, OK, OK])
        c = ClienteAPI(api, max_tentativas=3, dormir=lambda _: None)

        gen = (x for x in [3, 1, 3, fake_api.MAX_ID + 5, 2, 1])
        res = c.obter_varios(gen)
        self.assertEqual(list(res.keys()), [3, 1, fake_api.MAX_ID + 5, 2])
        self.assertEqual(res[3], {"id": 3, "nome": "Usuario 3"})
        self.assertEqual(res[1], {"id": 1, "nome": "Usuario 1"})
        self.assertIsNone(res[fake_api.MAX_ID + 5])
        self.assertEqual(res[2], {"id": 2, "nome": "Usuario 2"})
        # 1 retry on 3 (2 calls) + 1 call for 1 + 1 call for 1005 + 1 call for 2 = 5 calls
        self.assertEqual(len(api.chamadas), 5)

    def test_obter_varios_valida_todos_antes_de_requisitar(self):
        api = FakeAPI()
        c = ClienteAPI(api, dormir=lambda _: None)
        gen = (x for x in [1, 2, 0])
        with self.assertRaises(ValueError):
            c.obter_varios(gen)
        self.assertEqual(api.chamadas, [])

    def test_obter_varios_propaga_erro_api_e_falha_permanente(self):
        api = FakeAPI(roteiro=[OK, ERRO_500, ERRO_500])
        c = ClienteAPI(api, max_tentativas=2, dormir=lambda _: None)
        with self.assertRaises(FalhaPermanente):
            c.obter_varios([1, 2])


if __name__ == "__main__":
    unittest.main()
