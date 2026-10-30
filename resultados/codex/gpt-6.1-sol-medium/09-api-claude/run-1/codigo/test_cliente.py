import unittest

from cliente import ClienteAPI, ErroAPI, FalhaPermanente, NaoEncontrado
from fake_api import ErroConexao, FakeAPI, Resposta, TempoEsgotado


class APIComRoteiro:
    def __init__(self, eventos):
        self.eventos = iter(eventos)
        self.chamadas = []

    def requisitar(self, metodo, caminho, timeout):
        self.chamadas.append((metodo, caminho, timeout))
        evento = next(self.eventos)
        if isinstance(evento, Exception):
            raise evento
        return evento


class TestCliente(unittest.TestCase):
    def test_validacao_configuracao(self):
        for config in ({"max_tentativas": 0}, {"timeout": 0},
                       {"timeout": -1}, {"backoff_base": -1},
                       {"backoff_max": -1}, {"orcamento_espera": -1}):
            with self.subTest(config=config), self.assertRaises(ValueError):
                ClienteAPI(FakeAPI(), **config)

    def test_ids_invalidos_sem_requisicoes(self):
        api = FakeAPI(roteiro=[])
        cliente = ClienteAPI(api)
        for valor in (True, False, 0, -1, 1.0, "1", None, [], {}):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                cliente.obter_usuario(valor)
            with self.assertRaises(ValueError):
                cliente.obter_varios(iter([1, 2, valor]))
        self.assertEqual(api.chamadas, [])

    def test_sucesso_apos_falhas_e_timeout(self):
        api = FakeAPI(roteiro=["500", "conexao", "lento", "ok"])
        esperas = []
        cliente = ClienteAPI(api, timeout=1, dormir=esperas.append)
        self.assertEqual(cliente.obter_usuario(7), {"id": 7, "nome": "Usuario 7"})
        self.assertEqual(esperas, [0.5, 1, 2])
        self.assertEqual(api.chamadas, [("GET", "/usuarios/7", 1)] * 4)

    def test_status_sem_retry(self):
        for status in (404, 400, 403, 301, 501):
            with self.subTest(status=status):
                api = APIComRoteiro([Resposta(status)])
                esperas = []
                classe = NaoEncontrado if status == 404 else ErroAPI
                with self.assertRaises(classe) as ctx:
                    ClienteAPI(api, dormir=esperas.append).obter_usuario(1)
                self.assertEqual(ctx.exception.status, status)
                self.assertEqual(len(api.chamadas), 1)
                self.assertEqual(esperas, [])

    def test_todos_status_retentaveis(self):
        for status in (429, 500, 502, 503, 504):
            with self.subTest(status=status):
                api = APIComRoteiro([Resposta(status), Resposta(200, {"id": 1})])
                esperas = []
                self.assertEqual(
                    ClienteAPI(api, dormir=esperas.append).obter_usuario(1), {"id": 1})
                self.assertEqual(esperas, [0.5])

    def test_retry_after(self):
        for valor, esperado in (("2", 2), ("1.5", 1.5), ("100", 8),
                                ("0", 0), ("-1", 0.5), ("nan", 0.5),
                                ("inf", 0.5), ("abc", 0.5), (None, 0.5)):
            with self.subTest(valor=valor):
                api = APIComRoteiro([
                    Resposta(429, headers={"rEtRy-AfTeR": valor}),
                    Resposta(500), Resposta(200, {})])
                esperas = []
                ClienteAPI(api, dormir=esperas.append).obter_usuario(1)
                self.assertEqual(esperas, [esperado, 1])

    def test_causa_da_ultima_falha(self):
        for ultimo in (Resposta(503), ErroConexao("conexão"), TempoEsgotado("tempo")):
            with self.subTest(ultimo=ultimo):
                api = APIComRoteiro([ErroConexao(), ultimo])
                esperas = []
                with self.assertRaises(FalhaPermanente) as ctx:
                    ClienteAPI(api, max_tentativas=2,
                               dormir=esperas.append).obter_usuario(1)
                self.assertEqual(ctx.exception.tentativas, 2)
                self.assertIs(ctx.exception.__cause__,
                              ultimo if isinstance(ultimo, Exception) else None)
                self.assertEqual(esperas, [0.5])

    def test_excecao_nao_retentavel(self):
        erro = RuntimeError("falha inesperada")
        api = APIComRoteiro([erro])
        esperas = []
        with self.assertRaises(RuntimeError) as ctx:
            ClienteAPI(api, dormir=esperas.append).obter_usuario(1)
        self.assertIs(ctx.exception, erro)
        self.assertEqual(esperas, [])

    def test_orcamento_inclusive_e_reiniciado(self):
        api = FakeAPI(roteiro=["500", "500", "ok", "500", "500", "ok"])
        esperas = []
        cliente = ClienteAPI(api, dormir=esperas.append, orcamento_espera=1.5)
        cliente.obter_usuario(1)
        cliente.obter_usuario(2)
        self.assertEqual(esperas, [0.5, 1, 0.5, 1])

    def test_orcamento_esgotado(self):
        for ultimo in (Resposta(429, headers={"Retry-After": "2"}), ErroConexao()):
            with self.subTest(ultimo=ultimo):
                api = APIComRoteiro([ultimo])
                esperas = []
                with self.assertRaises(FalhaPermanente) as ctx:
                    ClienteAPI(api, orcamento_espera=0,
                               dormir=esperas.append).obter_usuario(1)
                self.assertEqual(ctx.exception.tentativas, 1)
                self.assertIs(ctx.exception.__cause__,
                              ultimo if isinstance(ultimo, Exception) else None)
                self.assertEqual(esperas, [])

    def test_milhares_de_tentativas(self):
        for base, teto in ((0.5, 8), (0, 8), (2, 0), (1e308, 1.7e308)):
            with self.subTest(base=base, teto=teto):
                api = APIComRoteiro([Resposta(500)] * 2000)
                esperas = []
                with self.assertRaises(FalhaPermanente) as ctx:
                    ClienteAPI(api, max_tentativas=2000, backoff_base=base,
                               backoff_max=teto, dormir=esperas.append).obter_usuario(1)
                self.assertEqual(ctx.exception.tentativas, 2000)
                self.assertEqual(len(esperas), 1999)
                self.assertTrue(all(0 <= espera <= teto for espera in esperas))
                self.assertEqual(esperas[-1], teto if base else 0)

    def test_uma_tentativa_sem_espera(self):
        esperas = []
        with self.assertRaises(FalhaPermanente) as ctx:
            ClienteAPI(FakeAPI(roteiro=["500"]), max_tentativas=1,
                       dormir=esperas.append).obter_usuario(1)
        self.assertEqual(ctx.exception.tentativas, 1)
        self.assertEqual(esperas, [])

    def test_varios_ordem_duplicados_e_404(self):
        api = FakeAPI(roteiro=[])
        cliente = ClienteAPI(api)
        resultado = cliente.obter_varios(i for i in (7, 1001, 7, 2, 1001))
        self.assertEqual(list(resultado), [7, 1001, 2])
        self.assertIsNone(resultado[1001])
        self.assertEqual(resultado[2]["id"], 2)
        self.assertEqual(len(api.chamadas), 3)
        self.assertEqual(cliente.obter_varios(iter([])), {})

    def test_varios_propaga_erros(self):
        for status, classe in ((500, FalhaPermanente), (403, ErroAPI)):
            with self.subTest(status=status):
                api = APIComRoteiro([Resposta(status)])
                with self.assertRaises(classe):
                    ClienteAPI(api, max_tentativas=1).obter_varios([1, 2])
                self.assertEqual(len(api.chamadas), 1)


if __name__ == "__main__":
    unittest.main()
