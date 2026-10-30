import time
import unittest
from unittest.mock import Mock, call, patch

from cliente import TempoEsgotado, baixar_pedidos
from loja_api import LojaAPI, LojaErroCliente, LojaIndisponivel, payload_pedido


class ClienteTests(unittest.TestCase):
    def test_ordem_payload_e_repeticoes(self):
        api = LojaAPI(7)
        ids = ["b", "a", "b", "flaky-missing-x"]
        self.assertEqual(
            baixar_pedidos(api, ids), [payload_pedido(7, id_) for id_ in ids]
        )
        self.assertEqual(api.tentativas("b"), 2)
        self.assertEqual(api.tentativas("flaky-missing-x"), 3)

    def test_backoff_exponencial_ate_sucesso(self):
        api = LojaAPI(2)
        with patch("cliente.time.sleep") as dormir:
            baixar_pedidos(api, ["flaky-x"], backoff_s=0.25)
        self.assertEqual(dormir.call_args_list, [call(0.25), call(0.5), call(1.0)])
        self.assertEqual(api.tentativas("flaky-x"), 4)

    def test_indisponibilidade_final_interrompe_lista(self):
        api = LojaAPI(0)
        with patch("cliente.time.sleep") as dormir:
            with self.assertRaises(LojaIndisponivel):
                baixar_pedidos(api, ["down-x", "seguinte"], max_tentativas=3,
                              backoff_s=0.1)
        self.assertEqual(dormir.call_args_list, [call(0.1), call(0.2)])
        self.assertEqual(api.tentativas("down-x"), 3)
        self.assertEqual(api.tentativas("seguinte"), 0)

    def test_erro_cliente_nao_repete_nem_dorme(self):
        for pedido_id in ("missing-down-x", "", None, 42, []):
            with self.subTest(pedido_id=pedido_id):
                api = Mock(wraps=LojaAPI(0))
                with patch("cliente.time.sleep") as dormir:
                    with self.assertRaises(LojaErroCliente):
                        baixar_pedidos(api, [pedido_id, "seguinte"], backoff_s=1)
                api.obter_pedido.assert_called_once_with(pedido_id)
                dormir.assert_not_called()

    def test_timeout_abandona_espera(self):
        api = LojaAPI(1)
        api.ATRASO_S = 0.5
        inicio = time.monotonic()
        with self.assertRaises(TempoEsgotado):
            baixar_pedidos(api, ["timeout-x", "seguinte"],
                          max_tentativas=2, timeout_s=0.02)
        self.assertLess(time.monotonic() - inicio, 0.3)
        self.assertEqual(api.tentativas("timeout-x"), 2)
        self.assertEqual(api.tentativas("seguinte"), 0)

    def test_slow_impar_sucesso_na_terceira_tentativa(self):
        api = LojaAPI(1)
        api.ATRASO_S = 0.5
        self.assertEqual(
            baixar_pedidos(api, ["slow-x"], timeout_s=0.02, max_tentativas=3),
            [payload_pedido(1, "slow-x")],
        )
        self.assertEqual(api.tentativas("slow-x"), 3)

    def test_ultima_falha_define_excecao(self):
        for falhas, esperado in (
            ([TempoEsgotado(), LojaIndisponivel()], LojaIndisponivel),
            ([LojaIndisponivel(), TempoEsgotado()], TempoEsgotado),
        ):
            with self.subTest(esperado=esperado):
                with patch("cliente._chamar_com_timeout", side_effect=falhas):
                    with self.assertRaises(esperado):
                        baixar_pedidos(Mock(), ["x"], max_tentativas=2)

    def test_validacao_antes_de_chamar_api(self):
        casos = [
            ({"ids": "x"}, TypeError),
            ({"ids": ("x",)}, TypeError),
            ({"ids": type("Lista", (list,), {})(["x"])}, TypeError),
            ({"max_tentativas": True}, TypeError),
            ({"max_tentativas": 1.5}, TypeError),
            ({"max_tentativas": 0}, ValueError),
            ({"backoff_s": True}, TypeError),
            ({"backoff_s": "0"}, TypeError),
            ({"backoff_s": -1}, ValueError),
            ({"timeout_s": False}, TypeError),
            ({"timeout_s": "1"}, TypeError),
            ({"timeout_s": 0}, ValueError),
            ({"timeout_s": -1}, ValueError),
        ]
        for argumentos, erro in casos:
            with self.subTest(argumentos=argumentos):
                api = Mock()
                kwargs = {"ids": ["x"], **argumentos}
                with self.assertRaises(erro):
                    baixar_pedidos(api, **kwargs)
                api.obter_pedido.assert_not_called()

    def test_lista_vazia_e_backoff_zero_nao_dormem(self):
        api = Mock()
        with patch("cliente.time.sleep") as dormir:
            self.assertEqual(baixar_pedidos(api, []), [])
            api.obter_pedido.assert_not_called()
            baixar_pedidos(LojaAPI(0), ["flaky-x"])
        dormir.assert_not_called()


if __name__ == "__main__":
    unittest.main()
