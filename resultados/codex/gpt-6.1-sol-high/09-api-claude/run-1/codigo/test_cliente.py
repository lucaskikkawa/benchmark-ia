import unittest

from cliente import ClienteAPI, ErroAPI, FalhaPermanente, NaoEncontrado
from fake_api import ErroConexao, FakeAPI, Resposta, TempoEsgotado


class APIRoteiro:
    def __init__(self, *eventos):
        self.eventos = iter(eventos)
        self.chamadas = []

    def requisitar(self, metodo, caminho, timeout):
        self.chamadas.append((metodo, caminho, timeout))
        evento = next(self.eventos)
        if isinstance(evento, Exception):
            raise evento
        return evento


class TestClienteAPI(unittest.TestCase):
    def test_validacao_configuracao(self):
        for parametro, valor in (("max_tentativas", 0), ("timeout", 0),
                                 ("timeout", -1), ("backoff_base", -1),
                                 ("backoff_max", -1), ("orcamento_espera", -1)):
            with self.subTest(parametro=parametro, valor=valor):
                with self.assertRaises(ValueError):
                    ClienteAPI(FakeAPI(), **{parametro: valor})

    def test_ids_invalidos_nao_requisitam(self):
        api = FakeAPI(roteiro=[])
        cliente = ClienteAPI(api)
        for invalido in (True, False, 0, -1, 1.0, "1", None, [], {}):
            with self.subTest(id=invalido):
                with self.assertRaises(ValueError):
                    cliente.obter_usuario(invalido)
                with self.assertRaises(ValueError):
                    cliente.obter_varios(iter([1, 2, invalido]))
        self.assertEqual(api.chamadas, [])

    def test_sucesso_timeout_e_backoff(self):
        api = FakeAPI(roteiro=["500", "503", "conexao", "lento", "ok"])
        esperas = []
        cliente = ClienteAPI(api, max_tentativas=5, backoff_max=2,
                             timeout=1, dormir=esperas.append)
        self.assertEqual(cliente.obter_usuario(7), {"id": 7, "nome": "Usuario 7"})
        self.assertEqual(esperas, [0.5, 1.0, 2, 2])
        self.assertEqual(api.chamadas, [("GET", "/usuarios/7", 1)] * 5)

    def test_status_sem_retry(self):
        for status in (404, 400, 403, 301, 501):
            with self.subTest(status=status):
                api = APIRoteiro(Resposta(status))
                esperas = []
                tipo = NaoEncontrado if status == 404 else ErroAPI
                with self.assertRaises(tipo) as capturado:
                    ClienteAPI(api, dormir=esperas.append).obter_usuario(1)
                self.assertEqual(capturado.exception.status, status)
                self.assertEqual(len(api.chamadas), 1)
                self.assertEqual(esperas, [])

    def test_status_retentaveis_e_causa_http(self):
        for status in (429, 500, 502, 503, 504):
            with self.subTest(status=status):
                api = APIRoteiro(Resposta(status), Resposta(status))
                esperas = []
                with self.assertRaises(FalhaPermanente) as capturado:
                    ClienteAPI(api, max_tentativas=2,
                               dormir=esperas.append).obter_usuario(1)
                self.assertEqual(capturado.exception.tentativas, 2)
                self.assertEqual(capturado.exception.status, status)
                self.assertIsNone(capturado.exception.__cause__)
                self.assertEqual(esperas, [0.5])

    def test_causa_da_ultima_falha(self):
        for erro in (ErroConexao("conexão"), TempoEsgotado("timeout")):
            with self.subTest(erro=erro):
                api = APIRoteiro(Resposta(500), erro)
                with self.assertRaises(FalhaPermanente) as capturado:
                    ClienteAPI(api, max_tentativas=2,
                               dormir=lambda s: None).obter_usuario(1)
                self.assertIs(capturado.exception.__cause__, erro)
                self.assertEqual(capturado.exception.tentativas, 2)
        api = APIRoteiro(ErroConexao(), Resposta(503))
        with self.assertRaises(FalhaPermanente) as capturado:
            ClienteAPI(api, max_tentativas=2, dormir=lambda s: None).obter_usuario(1)
        self.assertIsNone(capturado.exception.__cause__)

    def test_excecao_desconhecida_propaga(self):
        erro = RuntimeError("inesperado")
        api = APIRoteiro(erro)
        esperas = []
        with self.assertRaises(RuntimeError) as capturado:
            ClienteAPI(api, dormir=esperas.append).obter_usuario(1)
        self.assertIs(capturado.exception, erro)
        self.assertEqual(esperas, [])
        self.assertEqual(len(api.chamadas), 1)

    def test_retry_after(self):
        for valor, esperado in (("2", 2), ("1.5", 1.5), ("100", 8), ("0", 0),
                                 ("-1", 0.5), ("nan", 0.5), ("inf", 0.5),
                                 ("abc", 0.5), (None, 0.5)):
            with self.subTest(valor=valor):
                api = APIRoteiro(Resposta(429, headers={"rEtRy-AfTeR": valor}),
                                 Resposta(500), Resposta(200, {"id": 1}))
                esperas = []
                ClienteAPI(api, dormir=esperas.append).obter_usuario(1)
                self.assertEqual(esperas, [esperado, 1.0])

    def test_orcamento_igualdade_e_reinicio_por_chamada(self):
        api = FakeAPI(roteiro=["500", "ok", "500", "ok"])
        esperas = []
        cliente = ClienteAPI(api, orcamento_espera=0.5, dormir=esperas.append)
        cliente.obter_usuario(1)
        cliente.obter_usuario(2)
        self.assertEqual(esperas, [0.5, 0.5])

    def test_orcamento_esgotado(self):
        for evento in (Resposta(503), ErroConexao("conexão")):
            with self.subTest(evento=evento):
                api = APIRoteiro(Resposta(500), evento)
                esperas = []
                with self.assertRaises(FalhaPermanente) as capturado:
                    ClienteAPI(api, orcamento_espera=1,
                               dormir=esperas.append).obter_usuario(1)
                self.assertEqual(capturado.exception.tentativas, 2)
                self.assertEqual(esperas, [0.5])
                causa = evento if isinstance(evento, Exception) else None
                self.assertIs(capturado.exception.__cause__, causa)

    def test_uma_tentativa_e_orcamento_zero(self):
        for opcoes in ({"max_tentativas": 1}, {"orcamento_espera": 0}):
            api = APIRoteiro(Resposta(500))
            esperas = []
            with self.assertRaises(FalhaPermanente) as capturado:
                ClienteAPI(api, dormir=esperas.append, **opcoes).obter_usuario(1)
            self.assertEqual(capturado.exception.tentativas, 1)
            self.assertEqual(esperas, [])
        api = APIRoteiro(Resposta(500), Resposta(200, {}))
        esperas = []
        ClienteAPI(api, orcamento_espera=0, backoff_base=0,
                   dormir=esperas.append).obter_usuario(1)
        self.assertEqual(esperas, [0])

    def test_milhares_de_tentativas(self):
        for base, teto in ((0.5, 8), (0, 8), (0.5, 0), (1e-300, 1e300),
                          (0, 5e-324), (5e-324, 1e-320)):
            with self.subTest(base=base, teto=teto):
                api = APIRoteiro(*(Resposta(500) for _ in range(2000)))
                esperas = []
                with self.assertRaises(FalhaPermanente) as capturado:
                    ClienteAPI(api, max_tentativas=2000, backoff_base=base,
                               backoff_max=teto, dormir=esperas.append).obter_usuario(1)
                self.assertEqual(capturado.exception.tentativas, 2000)
                self.assertEqual(len(esperas), 1999)
                self.assertTrue(all(0 <= espera <= teto for espera in esperas))
                if base:
                    self.assertEqual(esperas[-1], teto)
                else:
                    self.assertTrue(all(espera == 0 for espera in esperas))

    def test_lote_ordem_duplicatas_e_ausentes(self):
        api = FakeAPI(roteiro=[])
        resultado = ClienteAPI(api).obter_varios(i for i in [3, 1001, 2, 3, 1001])
        self.assertEqual(list(resultado), [3, 1001, 2])
        self.assertEqual(resultado[3], {"id": 3, "nome": "Usuario 3"})
        self.assertIsNone(resultado[1001])
        self.assertEqual(len(api.chamadas), 3)
        self.assertEqual(ClienteAPI(api).obter_varios(iter([])), {})

    def test_lote_propaga_falhas(self):
        for status, tipo in ((503, FalhaPermanente), (403, ErroAPI)):
            api = APIRoteiro(Resposta(200, {"id": 1}), Resposta(status))
            with self.assertRaises(tipo):
                ClienteAPI(api, max_tentativas=1).obter_varios([1, 2, 3])
            self.assertEqual(len(api.chamadas), 2)


if __name__ == "__main__":
    unittest.main()
