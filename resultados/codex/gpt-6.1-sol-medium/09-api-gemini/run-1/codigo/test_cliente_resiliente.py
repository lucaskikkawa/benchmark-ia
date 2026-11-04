import unittest
from unittest.mock import Mock

from cliente_resiliente import ApiError, ClienteResiliente
from fake_api import ApiResponse, FakeApiServer, SimulatedNetworkError, SimulatedTimeoutError


class ClienteResilienteTests(unittest.TestCase):
    def test_sucesso_e_encaminhamento_dos_parametros(self):
        servidor = FakeApiServer()
        cliente = ClienteResiliente(servidor, timeout=4)
        payload = {"nome": "teste"}
        self.assertEqual(cliente.post("/dados", payload)["payload"], payload)
        self.assertEqual(servidor.chamadas, [
            {"metodo": "POST", "rota": "/dados", "payload": payload, "timeout": 4}
        ])
        self.assertEqual(cliente.get("/dados")["metodo"], "GET")

    def test_recuperacao_com_backoff(self):
        for tipo in ("network", "timeout", "503", "429"):
            with self.subTest(tipo=tipo):
                servidor = FakeApiServer()
                servidor.configurar_falhas("/dados", 2, tipo)
                esperas = []
                cliente = ClienteResiliente(servidor, sleep_fn=esperas.append)
                self.assertEqual(cliente.get("/dados")["status"], "ok")
                self.assertEqual(len(servidor.chamadas), 3)
                self.assertEqual(esperas, [0.05, 0.1])

    def test_esgotamento_e_status(self):
        for falha, status in [
            (SimulatedNetworkError("rede"), None),
            (SimulatedTimeoutError("timeout"), None),
            *[(ApiResponse(codigo, {}), codigo) for codigo in (429, 500, 502, 503, 504, 599)],
        ]:
            with self.subTest(falha=falha):
                servidor = Mock()
                if isinstance(falha, Exception):
                    servidor.requisicao.side_effect = falha
                else:
                    servidor.requisicao.return_value = falha
                esperas = []
                cliente = ClienteResiliente(servidor, sleep_fn=esperas.append)
                with self.assertRaises(ApiError) as contexto:
                    cliente.get("/dados")
                self.assertEqual(contexto.exception.status_code, status)
                self.assertEqual(servidor.requisicao.call_count, 3)
                self.assertEqual(esperas, [0.05, 0.1])

    def test_erros_definitivos_nao_repetem(self):
        for status in (199, 300, 301, 400, 401, 403, 404, 499, 600):
            with self.subTest(status=status):
                servidor = FakeApiServer()
                servidor.configurar_resposta("/dados", status, {})
                espera = Mock()
                with self.assertRaises(ApiError) as contexto:
                    ClienteResiliente(servidor, sleep_fn=espera).get("/dados")
                self.assertEqual(contexto.exception.status_code, status)
                self.assertEqual(len(servidor.chamadas), 1)
                espera.assert_not_called()

    def test_uma_tentativa_sem_espera(self):
        servidor = FakeApiServer()
        servidor.configurar_falhas("/dados", 1)
        espera = Mock()
        with self.assertRaises(ApiError):
            ClienteResiliente(servidor, max_tentativas=1, sleep_fn=espera).get("/dados")
        espera.assert_not_called()

    def test_validacao(self):
        for valor in (True, False, 0, -1, 1.5, "3", None):
            with self.subTest(max_tentativas=valor), self.assertRaises(ValueError):
                ClienteResiliente(FakeApiServer(), max_tentativas=valor)
        for parametro in ("backoff_base", "backoff_fator", "timeout"):
            for valor in (True, False, 0, -1, "1", None, 1j, float("nan")):
                with self.subTest(parametro=parametro, valor=valor), self.assertRaises(ValueError):
                    ClienteResiliente(FakeApiServer(), **{parametro: valor})

    def test_excecao_preserva_mensagem(self):
        erro = ApiError("mensagem")
        self.assertEqual(str(erro), "mensagem")
        self.assertIsNone(erro.status_code)


if __name__ == "__main__":
    unittest.main()
