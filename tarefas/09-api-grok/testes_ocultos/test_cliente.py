import time

import pytest

from cliente import TempoEsgotado, baixar_pedidos
from loja_api import LojaAPI, LojaErroCliente, LojaIndisponivel, payload_pedido


def test_lista_vazia_nao_chama_api():
    api = LojaAPI(0)
    assert baixar_pedidos(api, []) == []
    assert api.tentativas("qualquer") == 0


def test_pedidos_normais_preservam_ordem_e_corpo():
    api = LojaAPI(7)
    ids = ["p-2", "p-1", "alfa"]
    obtidos = baixar_pedidos(api, ids, timeout_s=1)
    assert obtidos == [payload_pedido(7, item) for item in ids]
    assert [item["id"] for item in obtidos] == ids
    assert all(api.tentativas(item) == 1 for item in ids)


def test_seed_diferente_muda_o_total():
    um = baixar_pedidos(LojaAPI(1), ["pedido"], timeout_s=1)
    dois = baixar_pedidos(LojaAPI(2), ["pedido"], timeout_s=1)
    assert um[0]["total_centavos"] != dois[0]["total_centavos"]
    assert um[0] == payload_pedido(1, "pedido")


def test_flaky_seed_0_e_seed_1():
    api = LojaAPI(0)
    obtido = baixar_pedidos(api, ["flaky-a"], max_tentativas=5, backoff_s=0, timeout_s=1)
    assert obtido == [payload_pedido(0, "flaky-a")]
    assert api.tentativas("flaky-a") == 2

    api = LojaAPI(1)
    obtido = baixar_pedidos(api, ["flaky-b"], max_tentativas=5, backoff_s=0, timeout_s=1)
    assert obtido == [payload_pedido(1, "flaky-b")]
    assert api.tentativas("flaky-b") == 3


def test_flaky_seed_2_no_limite_e_abaixo():
    api = LojaAPI(2)
    with pytest.raises(LojaIndisponivel):
        baixar_pedidos(api, ["flaky-c"], max_tentativas=3, backoff_s=0, timeout_s=1)
    assert api.tentativas("flaky-c") == 3

    api = LojaAPI(2)
    obtido = baixar_pedidos(api, ["flaky-c"], max_tentativas=4, backoff_s=0, timeout_s=1)
    assert obtido == [payload_pedido(2, "flaky-c")]
    assert api.tentativas("flaky-c") == 4


def test_missing_nao_repete_e_interrompe_a_lista():
    api = LojaAPI(0)
    with pytest.raises(LojaErroCliente):
        baixar_pedidos(
            api,
            ["ok", "missing-z", "depois"],
            max_tentativas=4,
            backoff_s=0,
            timeout_s=1,
        )
    assert api.tentativas("ok") == 1
    assert api.tentativas("missing-z") == 1
    assert api.tentativas("depois") == 0


def test_down_estorra_tentativas():
    api = LojaAPI(4)
    with pytest.raises(LojaIndisponivel):
        baixar_pedidos(api, ["ok", "down-x"], max_tentativas=4, backoff_s=0, timeout_s=1)
    assert api.tentativas("ok") == 1
    assert api.tentativas("down-x") == 4
    assert api.tentativas("nunca") == 0


def test_slow_nao_espera_o_atraso_inteiro():
    api = LojaAPI(0)
    inicio = time.perf_counter()
    obtido = baixar_pedidos(
        api,
        ["slow-1"],
        max_tentativas=4,
        backoff_s=0,
        timeout_s=0.15,
    )
    gasto = time.perf_counter() - inicio
    assert obtido == [payload_pedido(0, "slow-1")]
    assert api.tentativas("slow-1") == 2
    assert gasto < LojaAPI.ATRASO_S * 0.75


def test_timeout_permanente_levanta_tempo_esgotado():
    api = LojaAPI(3)
    inicio = time.perf_counter()
    with pytest.raises(TempoEsgotado):
        baixar_pedidos(
            api,
            ["timeout-z"],
            max_tentativas=3,
            backoff_s=0,
            timeout_s=0.15,
        )
    gasto = time.perf_counter() - inicio
    assert api.tentativas("timeout-z") == 3
    assert gasto < LojaAPI.ATRASO_S * 0.75


def test_mistura_normal_e_flaky_na_ordem():
    api = LojaAPI(0)
    ids = ["a", "flaky-m", "b"]
    obtido = baixar_pedidos(api, ids, max_tentativas=5, backoff_s=0, timeout_s=1)
    assert obtido == [payload_pedido(0, item) for item in ids]
    assert api.tentativas("a") == 1
    assert api.tentativas("flaky-m") == 2
    assert api.tentativas("b") == 1


def test_backoff_exponencial_soma_tres_passos():
    api = LojaAPI(1)
    inicio = time.perf_counter()
    baixar_pedidos(
        api,
        ["flaky-bk"],
        max_tentativas=5,
        backoff_s=0.15,
        timeout_s=1,
    )
    gasto = time.perf_counter() - inicio
    assert api.tentativas("flaky-bk") == 3
    assert gasto >= 0.35
    assert gasto < 2.0


def test_argumentos_invalidos_nao_chamam_api():
    api = LojaAPI(0)
    with pytest.raises(ValueError):
        baixar_pedidos(api, [], max_tentativas=0)
    with pytest.raises(TypeError):
        baixar_pedidos(api, [], max_tentativas=True)
    with pytest.raises(TypeError):
        baixar_pedidos(api, "abc")
    with pytest.raises(ValueError):
        baixar_pedidos(api, ["a"], timeout_s=0)
    with pytest.raises(ValueError):
        baixar_pedidos(api, ["a"], backoff_s=-0.1)
    assert api.tentativas("a") == 0
    assert api.tentativas("abc") == 0


def test_max_tentativas_1_no_pedido_normal():
    api = LojaAPI(9)
    obtido = baixar_pedidos(api, ["solo"], max_tentativas=1, backoff_s=0, timeout_s=1)
    assert obtido == [payload_pedido(9, "solo")]
    assert api.tentativas("solo") == 1


def test_id_repetido_nao_usa_cache():
    api = LojaAPI(4)
    ids = ["p", "p", "q"]
    obtido = baixar_pedidos(api, ids, max_tentativas=3, backoff_s=0, timeout_s=1)
    assert obtido == [payload_pedido(4, item) for item in ids]
    assert api.tentativas("p") == 2
    assert api.tentativas("q") == 1


def test_prefixo_e_id_vazio_nao_repete():
    api = LojaAPI(0)
    with pytest.raises(LojaErroCliente):
        baixar_pedidos(
            api,
            ["missing-down-x", "depois"],
            max_tentativas=4,
            backoff_s=0.2,
            timeout_s=1,
        )
    assert api.tentativas("missing-down-x") == 1
    assert api.tentativas("depois") == 0

    api = LojaAPI(0)
    inicio = time.perf_counter()
    with pytest.raises(LojaErroCliente):
        baixar_pedidos(api, [""], max_tentativas=4, backoff_s=0.2, timeout_s=1)
    assert time.perf_counter() - inicio < 0.15

    api = LojaAPI(0)
    obtido = baixar_pedidos(
        api,
        ["flaky-missing-x"],
        max_tentativas=4,
        backoff_s=0,
        timeout_s=1,
    )
    assert obtido == [payload_pedido(0, "flaky-missing-x")]
    assert api.tentativas("flaky-missing-x") == 2


def test_slow_seed_impar_duas_esperas():
    api = LojaAPI(1)
    inicio = time.perf_counter()
    obtido = baixar_pedidos(
        api,
        ["slow-1"],
        max_tentativas=4,
        backoff_s=0,
        timeout_s=0.15,
    )
    gasto = time.perf_counter() - inicio
    assert obtido == [payload_pedido(1, "slow-1")]
    assert api.tentativas("slow-1") == 3
    assert gasto < LojaAPI.ATRASO_S * 0.75


def test_timeout_interrompe_o_resto_e_uma_tentativa():
    api = LojaAPI(0)
    inicio = time.perf_counter()
    with pytest.raises(TempoEsgotado):
        baixar_pedidos(
            api,
            ["timeout-z", "depois"],
            max_tentativas=2,
            backoff_s=0,
            timeout_s=0.15,
        )
    assert api.tentativas("timeout-z") == 2
    assert api.tentativas("depois") == 0
    assert time.perf_counter() - inicio < LojaAPI.ATRASO_S * 0.75

    api = LojaAPI(0)
    inicio = time.perf_counter()
    with pytest.raises(TempoEsgotado):
        baixar_pedidos(
            api,
            ["slow-x", "nao"],
            max_tentativas=1,
            backoff_s=0.2,
            timeout_s=0.15,
        )
    assert api.tentativas("slow-x") == 1
    assert api.tentativas("nao") == 0
    assert time.perf_counter() - inicio < 0.45


def test_tuple_e_backoff_de_uma_falha():
    api = LojaAPI(0)
    with pytest.raises(TypeError):
        baixar_pedidos(api, ("a", "b"))
    with pytest.raises(TypeError):
        baixar_pedidos(api, [], max_tentativas=1.5)
    assert api.tentativas("a") == 0

    inicio = time.perf_counter()
    obtido = baixar_pedidos(
        api,
        ["flaky-once"],
        max_tentativas=5,
        backoff_s=0.25,
        timeout_s=1,
    )
    gasto = time.perf_counter() - inicio
    assert obtido == [payload_pedido(0, "flaky-once")]
    assert api.tentativas("flaky-once") == 2
    assert gasto >= 0.2
    assert gasto < 0.55
