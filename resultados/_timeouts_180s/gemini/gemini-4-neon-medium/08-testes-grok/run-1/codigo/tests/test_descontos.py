"""Suíte de testes para descontos.aplicar_desconto."""

from datetime import date, datetime
from decimal import Decimal

import pytest

from descontos import aplicar_desconto


CHAVES_ESPERADAS = {"preco_final", "desconto", "cupom_aplicado"}


def assert_resultado(resultado, preco_original, preco_final, cupom_aplicado):
    assert type(resultado) is dict
    assert set(resultado.keys()) == CHAVES_ESPERADAS
    assert type(resultado["preco_final"]) is int
    assert type(resultado["desconto"]) is int
    if cupom_aplicado is None:
        assert resultado["cupom_aplicado"] is None
    else:
        assert type(resultado["cupom_aplicado"]) is str
        assert resultado["cupom_aplicado"] == cupom_aplicado
    assert resultado["preco_final"] == preco_final
    assert resultado["desconto"] == preco_original - preco_final
    assert 0 <= resultado["preco_final"] <= preco_original
    assert 0 <= resultado["desconto"] <= preco_original


# ---------------------------------------------------------------------------
# Sem cupom (None e "")
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cupom", [None, ""])
@pytest.mark.parametrize("preco", [0, 1, 99, 100, 500, 123456])
def test_sem_cupom_nao_altera_preco(cupom, preco):
    res = aplicar_desconto(preco, cupom, "2024-06-15")
    assert_resultado(res, preco, preco, None)


def test_chamada_com_argumentos_nomeados():
    res = aplicar_desconto(preco_centavos=200, cupom="OFF10", hoje="2024-06-15")
    assert_resultado(res, 200, 180, "OFF10")


# ---------------------------------------------------------------------------
# OFF10
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (2, 1),
        (9, 8),
        (10, 9),
        (11, 9),
        (15, 13),
        (19, 17),
        (99, 89),
        (100, 90),
        (101, 90),
        (109, 98),
        (200, 180),
        (1000, 900),
        (10**18 + 10, ((10**18 + 10) * 90) // 100),
    ],
)
def test_off10_calculo_com_piso(preco, esperado):
    res = aplicar_desconto(preco, "OFF10", "2024-06-15")
    assert_resultado(res, preco, esperado, "OFF10")


@pytest.mark.parametrize(
    "hoje",
    ["0001-01-01", "2000-02-29", "2023-12-31", "2024-12-25", "2025-07-04", "9999-12-31"],
)
def test_off10_independe_da_data(hoje):
    res = aplicar_desconto(101, "OFF10", hoje)
    assert_resultado(res, 101, 90, "OFF10")


# ---------------------------------------------------------------------------
# OFF5
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (2, 1),
        (19, 18),
        (20, 19),
        (21, 19),
        (99, 94),
        (100, 95),
        (101, 95),
        (199, 189),
        (200, 190),
        (1000, 950),
        (10**18 + 20, ((10**18 + 20) * 95) // 100),
    ],
)
def test_off5_calculo_com_piso(preco, esperado):
    res = aplicar_desconto(preco, "OFF5", "2024-06-15")
    assert_resultado(res, preco, esperado, "OFF5")


@pytest.mark.parametrize(
    "hoje",
    ["0001-01-01", "2023-05-10", "2024-12-25", "2026-01-01", "9999-12-31"],
)
def test_off5_independe_da_data(hoje):
    res = aplicar_desconto(101, "OFF5", hoje)
    assert_resultado(res, 101, 95, "OFF5")


# ---------------------------------------------------------------------------
# FIXO500
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (100, 0),
        (499, 0),
        (500, 0),
        (501, 1),
        (502, 2),
        (1000, 500),
        (10000, 9500),
    ],
)
def test_fixo500_com_piso_zero(preco, esperado):
    res = aplicar_desconto(preco, "FIXO500", "2024-06-15")
    assert_resultado(res, preco, esperado, "FIXO500")


def test_fixo500_piso_desconto_igual_ao_preco():
    res = aplicar_desconto(100, "FIXO500", "2024-06-15")
    assert res == {"preco_final": 0, "desconto": 100, "cupom_aplicado": "FIXO500"}


def test_fixo500_preco_zero_conta_como_aplicado():
    res = aplicar_desconto(0, "FIXO500", "2024-06-15")
    assert res == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "FIXO500"}


@pytest.mark.parametrize("hoje", ["0001-01-01", "2023-12-31", "2025-01-01", "9999-12-31"])
def test_fixo500_independe_da_data(hoje):
    res = aplicar_desconto(750, "FIXO500", hoje)
    assert_resultado(res, 750, 250, "FIXO500")


# ---------------------------------------------------------------------------
# BEMVINDO (2024-01-01 a 2024-12-31 inclusive)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hoje",
    [
        "2024-01-01",
        "2024-01-02",
        "2024-02-29",
        "2024-06-15",
        "2024-12-25",
        "2024-12-30",
        "2024-12-31",
    ],
)
def test_bemvindo_dentro_da_janela(hoje):
    res = aplicar_desconto(101, "BEMVINDO", hoje)
    assert_resultado(res, 101, 80, "BEMVINDO")


@pytest.mark.parametrize(
    "hoje",
    [
        "0001-01-01",
        "2023-01-01",
        "2023-06-15",
        "2023-12-30",
        "2023-12-31",
        "2025-01-01",
        "2025-01-02",
        "2025-12-31",
        "9999-12-31",
    ],
)
def test_bemvindo_fora_da_janela(hoje):
    res = aplicar_desconto(1000, "BEMVINDO", hoje)
    assert_resultado(res, 1000, 1000, None)


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (2, 1),
        (4, 3),
        (5, 4),
        (99, 79),
        (100, 80),
        (101, 80),
        (199, 159),
        (250, 200),
        (10**18 + 5, ((10**18 + 5) * 80) // 100),
    ],
)
def test_bemvindo_calculo_com_piso(preco, esperado):
    res = aplicar_desconto(preco, "BEMVINDO", "2024-07-01")
    assert_resultado(res, preco, esperado, "BEMVINDO")


def test_bemvindo_fora_da_janela_preco_zero():
    res = aplicar_desconto(0, "BEMVINDO", "2025-01-01")
    assert_resultado(res, 0, 0, None)


# ---------------------------------------------------------------------------
# NATAL (24 e 25 de dezembro em qualquer ano 1..9999)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hoje",
    [
        "0001-12-24",
        "0001-12-25",
        "1900-12-24",
        "1900-12-25",
        "2000-12-24",
        "2000-12-25",
        "2023-12-24",
        "2023-12-25",
        "2024-12-24",
        "2024-12-25",
        "2025-12-24",
        "2025-12-25",
        "2099-12-24",
        "2099-12-25",
        "9999-12-24",
        "9999-12-25",
    ],
)
def test_natal_em_24_e_25_de_dezembro(hoje):
    res = aplicar_desconto(101, "NATAL", hoje)
    assert_resultado(res, 101, 85, "NATAL")


@pytest.mark.parametrize(
    "hoje",
    [
        "0001-12-23",
        "0001-12-26",
        "2024-01-24",
        "2024-01-25",
        "2024-06-24",
        "2024-06-25",
        "2024-11-24",
        "2024-11-25",
        "2024-12-01",
        "2024-12-23",
        "2024-12-26",
        "2024-12-31",
        "2025-12-23",
        "2025-12-26",
        "9999-12-23",
        "9999-12-26",
    ],
)
def test_natal_fora_da_janela(hoje):
    res = aplicar_desconto(1000, "NATAL", hoje)
    assert_resultado(res, 1000, 1000, None)


@pytest.mark.parametrize("dia", ["2024-12-24", "2024-12-25"])
@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (2, 1),
        (7, 5),
        (19, 16),
        (20, 17),
        (99, 84),
        (100, 85),
        (101, 85),
        (199, 169),
        (1000, 850),
        (10**18 + 20, ((10**18 + 20) * 85) // 100),
    ],
)
def test_natal_calculo_com_piso(dia, preco, esperado):
    res = aplicar_desconto(preco, "NATAL", dia)
    assert_resultado(res, preco, esperado, "NATAL")


def test_natal_fora_da_janela_preco_zero():
    res = aplicar_desconto(0, "NATAL", "2024-12-26")
    assert_resultado(res, 0, 0, None)


# ---------------------------------------------------------------------------
# Validação de preco_centavos
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco_invalido",
    [
        True,
        False,
        0.0,
        100.0,
        100.5,
        -1.0,
        float("inf"),
        float("nan"),
        "100",
        "0",
        "",
        None,
        Decimal("100"),
        [100],
        {"preco": 100},
        1 + 0j,
    ],
)
def test_preco_tipo_invalido_levanta_type_error(preco_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(preco_invalido, "OFF10", "2024-06-15")


@pytest.mark.parametrize("cupom", [None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL"])
@pytest.mark.parametrize("preco_negativo", [-1, -100, -500, -10**9])
def test_preco_negativo_levanta_value_error(cupom, preco_negativo):
    with pytest.raises(ValueError):
        aplicar_desconto(preco_negativo, cupom, "2024-12-25")


def test_preco_bool_com_cupom_none_levanta_type_error():
    with pytest.raises(TypeError):
        aplicar_desconto(False, None, "2024-06-15")
    with pytest.raises(TypeError):
        aplicar_desconto(True, None, "2024-06-15")


# ---------------------------------------------------------------------------
# Validação de cupom
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cupom_invalido",
    [
        0,
        10,
        10.0,
        True,
        False,
        b"OFF10",
        b"",
        [],
        ["OFF10"],
        {},
        ("OFF10",),
    ],
)
def test_cupom_tipo_invalido_levanta_type_error(cupom_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(100, cupom_invalido, "2024-06-15")


@pytest.mark.parametrize(
    "cupom_desconhecido",
    [
        " ",
        "  ",
        "\t",
        "\n",
        "\r",
        " \t\n ",
        " OFF10",
        "OFF10 ",
        " OFF10 ",
        "\tOFF10",
        "OFF10\n",
        "off10",
        "Off10",
        "oFf10",
        " OFF5",
        "OFF5 ",
        "off5",
        " FIXO500",
        "FIXO500 ",
        "fixo500",
        " BEMVINDO",
        "BEMVINDO ",
        "bemvindo",
        " NATAL",
        "NATAL ",
        "natal",
        "OFF15",
        "OFF20",
        "OFF0",
        "FIXO100",
        "NATAL2024",
        "BEMVINDO2024",
        "DESCONHECIDO",
        "None",
        "NONE",
        "null",
    ],
)
def test_cupom_desconhecido_ou_sem_normalizacao_levanta_value_error(cupom_desconhecido):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom_desconhecido, "2024-12-25")


# ---------------------------------------------------------------------------
# Validação de hoje (tipo, formato e calendário gregoriano)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hoje_invalido",
    [
        None,
        date(2024, 6, 15),
        datetime(2024, 6, 15, 12, 0),
        20240615,
        2024.06,
        True,
        False,
        b"2024-06-15",
        ["2024-06-15"],
    ],
)
def test_hoje_tipo_invalido_levanta_type_error(hoje_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(100, "OFF10", hoje_invalido)


@pytest.mark.parametrize(
    "hoje_invalido",
    [
        "",
        " ",
        "2024",
        "2024-01",
        "2024-1-1",
        "2024-01-1",
        "2024-1-01",
        "24-01-01",
        "999-12-25",
        "1-01-01",
        "02024-01-01",
        "10000-01-01",
        " 2024-01-01",
        "2024-01-01 ",
        "2024-01-01\n",
        "2024-01-01T00:00:00",
        "2024-01-01 00:00:00",
        "2024/01/01",
        "2024.01.01",
        "20240101",
        "2024_01_01",
        "2024 01 01",
        "2024-01/01",
        "2024/01-01",
        "01-01-2024",
        "25-12-2024",
        "2024-25-12",
        "abcd-ef-gh",
        "2024-ab-01",
        "2024-01-ab",
        "-001-01-01",
        "+202-01-01",
        # Datas inexistentes no calendário gregoriano
        "0000-01-01",
        "0000-12-25",
        "2024-00-10",
        "2024-13-01",
        "2024-01-00",
        "2024-01-32",
        "2024-02-30",
        "2024-02-31",
        "2024-04-31",
        "2024-06-31",
        "2024-09-31",
        "2024-11-31",
        # 29 de fevereiro em anos não bissextos (incluindo regra do século)
        "0001-02-29",
        "0100-02-29",
        "1800-02-29",
        "1900-02-29",
        "2021-02-29",
        "2023-02-29",
        "2025-02-29",
        "2100-02-29",
        "2200-02-29",
        "9900-02-29",
        "9999-02-29",
    ],
)
def test_hoje_invalido_levanta_value_error(hoje_invalido):
    with pytest.raises(ValueError):
        aplicar_desconto(100, "OFF10", hoje_invalido)


@pytest.mark.parametrize("cupom", [None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL"])
@pytest.mark.parametrize("hoje_invalido", ["1900-02-29", "2024-02-30", "2024/06/15"])
def test_hoje_e_validado_para_qualquer_cupom(cupom, hoje_invalido):
    with pytest.raises(ValueError):
        aplicar_desconto(100, cupom, hoje_invalido)


@pytest.mark.parametrize(
    "data_valida",
    [
        "0001-01-01",
        "0001-12-25",
        "0004-02-29",
        "0400-02-29",
        "1600-02-29",
        "2000-02-29",
        "2004-02-29",
        "2020-02-29",
        "2024-02-29",
        "2400-02-29",
        "9996-02-29",
        "9999-12-31",
    ],
)
def test_datas_bissextas_e_limites_validos(data_valida):
    res = aplicar_desconto(100, None, data_valida)
    assert_resultado(res, 100, 100, None)
