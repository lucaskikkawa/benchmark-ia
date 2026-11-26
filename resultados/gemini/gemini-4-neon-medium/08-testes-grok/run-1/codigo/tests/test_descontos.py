"""Suíte de testes para o módulo descontos."""

from datetime import date
from decimal import Decimal

import pytest

from descontos import aplicar_desconto


def _assert_resultado(res, preco_centavos, preco_final, cupom_aplicado):
    assert type(res) is dict
    assert set(res.keys()) == {"preco_final", "desconto", "cupom_aplicado"}
    assert type(res["preco_final"]) is int
    assert type(res["desconto"]) is int
    assert res["preco_final"] == preco_final
    assert res["desconto"] == preco_centavos - preco_final
    if cupom_aplicado is None:
        assert res["cupom_aplicado"] is None
    else:
        assert type(res["cupom_aplicado"]) is str
        assert res["cupom_aplicado"] == cupom_aplicado


# ---------------------------------------------------------------------------
# Validação de tipos e valores: preco_centavos
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco_invalido",
    [
        True,
        False,
        0.0,
        100.0,
        99.9,
        "100",
        "",
        None,
        [100],
        {"preco": 100},
        Decimal("100"),
    ],
)
@pytest.mark.parametrize("cupom", [None, "", "OFF10", "FIXO500", "BEMVINDO", "NATAL"])
def test_preco_tipo_invalido_levanta_type_error(preco_invalido, cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(preco_invalido, cupom, "2024-06-15")


@pytest.mark.parametrize("preco_negativo", [-1, -10, -100, -500, -10**9])
@pytest.mark.parametrize("cupom", [None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL"])
def test_preco_negativo_levanta_value_error(preco_negativo, cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(preco_negativo, cupom, "2024-06-15")


# ---------------------------------------------------------------------------
# Validação de tipos e valores: cupom
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cupom_tipo_invalido",
    [
        0,
        123,
        10.5,
        True,
        False,
        b"OFF10",
        ["OFF10"],
        {"codigo": "OFF10"},
        ("OFF10",),
    ],
)
def test_cupom_tipo_invalido_levanta_type_error(cupom_tipo_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom_tipo_invalido, "2024-06-15")


@pytest.mark.parametrize(
    "cupom_invalido",
    [
        # Espaços em branco não são vazios
        " ",
        "   ",
        "\t",
        "\n",
        "\r\n",
        # Sem strip()
        " OFF10",
        "OFF10 ",
        " OFF10 ",
        "\tOFF10",
        "OFF10\n",
        " OFF5",
        "OFF5 ",
        " FIXO500",
        "FIXO500 ",
        " BEMVINDO",
        "BEMVINDO ",
        " NATAL",
        "NATAL ",
        # Case-sensitive
        "off10",
        "Off10",
        "off5",
        "Off5",
        "fixo500",
        "Fixo500",
        "bemvindo",
        "BemVindo",
        "natal",
        "Natal",
        # Códigos desconhecidos
        "INVALIDO",
        "OFF0",
        "OFF15",
        "OFF20",
        "OFF100",
        "FIXO100",
        "FIXO50",
        "NATAL2024",
        "BEMVINDO2024",
        "NONE",
        "None",
        "null",
    ],
)
def test_cupom_desconhecido_ou_mal_formatado_levanta_value_error(cupom_invalido):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom_invalido, "2024-12-25")


# ---------------------------------------------------------------------------
# Validação de tipos e valores: hoje
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hoje_tipo_invalido",
    [
        None,
        date(2024, 6, 15),
        20240615,
        2024.06,
        True,
        False,
        b"2024-06-15",
        ["2024-06-15"],
    ],
)
@pytest.mark.parametrize("cupom", [None, "", "OFF10", "BEMVINDO", "NATAL"])
def test_hoje_tipo_invalido_levanta_type_error(hoje_tipo_invalido, cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom, hoje_tipo_invalido)


@pytest.mark.parametrize(
    "data_invalida",
    [
        # Formato errado
        "",
        " ",
        "2024-1-1",
        "2024-01-1",
        "2024-1-01",
        "24-01-01",
        "2024/01/01",
        "2024.01.01",
        "20240101",
        "2024-01/01",
        "2024/01-01",
        "01-01-2024",
        "31-12-2024",
        " 2024-01-01",
        "2024-01-01 ",
        "2024-01-01\n",
        "2024-01-01T00:00:00",
        "2024-W01-1",
        "+2024-01-01",
        "-2024-01-01",
        "abcd-ef-gh",
        "2024-aa-01",
        "2024--1-01",
        # Datas inexistentes no calendário gregoriano
        "0000-01-01",
        "0000-12-31",
        "2024-00-10",
        "2024-13-10",
        "2024-01-00",
        "2024-01-32",
        "2024-04-31",
        "2024-06-31",
        "2024-09-31",
        "2024-11-31",
        "2024-02-30",
        "2024-02-31",
        # 29 de fevereiro em anos não bissextos (incl. regra do século)
        "0001-02-29",
        "1800-02-29",
        "1900-02-29",
        "2100-02-29",
        "2200-02-29",
        "2300-02-29",
        "2023-02-29",
        "2025-02-29",
        "9999-02-29",
    ],
)
@pytest.mark.parametrize("cupom", [None, "", "OFF10", "FIXO500", "BEMVINDO", "NATAL"])
def test_hoje_invalido_levanta_value_error(data_invalida, cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom, data_invalida)


@pytest.mark.parametrize(
    "data_valida",
    [
        "0001-01-01",
        "0001-12-25",
        "1600-02-29",
        "1900-02-28",
        "2000-02-29",
        "2020-02-29",
        "2023-02-28",
        "2024-02-29",
        "2400-02-29",
        "9999-12-31",
    ],
)
def test_datas_gregorianas_validas_aceitas(data_valida):
    res = aplicar_desconto(1000, None, data_valida)
    _assert_resultado(res, 1000, 1000, None)


# ---------------------------------------------------------------------------
# Sem cupom: None e ""
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("cupom", [None, ""])
@pytest.mark.parametrize("preco", [0, 1, 50, 100, 500, 12345])
def test_sem_cupom_nao_altera_preco(cupom, preco):
    res = aplicar_desconto(preco, cupom, "2024-06-15")
    _assert_resultado(res, preco, preco, None)


# ---------------------------------------------------------------------------
# OFF10: (preco * 90) // 100
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),       # piso: (1 * 90) // 100 = 0 (não 1 - 1//10 = 1)
        (9, 8),       # (9 * 90) // 100 = 8 (não 9 - 0 = 9)
        (10, 9),
        (15, 13),     # (15 * 90) // 100 = 13 (não 15 - 1 = 14, nem round 14)
        (19, 17),
        (99, 89),     # (99 * 90) // 100 = 89 (não 99 - 9 = 90)
        (100, 90),
        (101, 90),
        (250, 225),
        (10**16 + 3, ((10**16 + 3) * 90) // 100),  # precisão inteira vs float
    ],
)
def test_off10_calculo_e_piso(preco, esperado):
    res = aplicar_desconto(preco, "OFF10", "2023-05-10")
    _assert_resultado(res, preco, esperado, "OFF10")


# ---------------------------------------------------------------------------
# OFF5: (preco * 95) // 100
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),       # (1 * 95) // 100 = 0 (não 1)
        (19, 18),     # (19 * 95) // 100 = 18 (não 19)
        (20, 19),
        (100, 95),
        (101, 95),    # (101 * 95) // 100 = 95 (não 96)
        (199, 189),
        (200, 190),
        (10**16 + 3, ((10**16 + 3) * 95) // 100),  # precisão inteira vs float
    ],
)
def test_off5_calculo_e_piso(preco, esperado):
    res = aplicar_desconto(preco, "OFF5", "2023-05-10")
    _assert_resultado(res, preco, esperado, "OFF5")


# ---------------------------------------------------------------------------
# FIXO500: max(0, preco - 500)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (100, 0),     # piso 0, desconto deve ser 100 (não 500, não negativo)
        (499, 0),
        (500, 0),
        (501, 1),
        (1000, 500),
        (1234, 734),
    ],
)
def test_fixo500_calculo_e_piso(preco, esperado):
    res = aplicar_desconto(preco, "FIXO500", "2023-05-10")
    _assert_resultado(res, preco, esperado, "FIXO500")


# ---------------------------------------------------------------------------
# BEMVINDO: (preco * 80) // 100 entre 2024-01-01 e 2024-12-31 inclusive
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "data_dentro",
    [
        "2024-01-01",  # extremo inicial inclusive
        "2024-01-02",
        "2024-02-29",  # ano bissexto
        "2024-06-15",
        "2024-12-30",
        "2024-12-31",  # extremo final inclusive
    ],
)
def test_bemvindo_dentro_da_janela(data_dentro):
    res = aplicar_desconto(1000, "BEMVINDO", data_dentro)
    _assert_resultado(res, 1000, 800, "BEMVINDO")


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),       # (1 * 80) // 100 = 0 (não 1 - 0 = 1)
        (4, 3),       # (4 * 80) // 100 = 3 (não 4 - 0 = 4)
        (5, 4),
        (7, 5),       # (7 * 80) // 100 = 5 (não 7 - 1 = 6, nem round 6)
        (100, 80),
        (103, 82),    # (103 * 80) // 100 = 82 (não 103 - 20 = 83)
        (10**16 + 3, ((10**16 + 3) * 80) // 100),  # precisão inteira vs float
    ],
)
def test_bemvindo_calculo_e_piso(preco, esperado):
    res = aplicar_desconto(preco, "BEMVINDO", "2024-01-01")
    _assert_resultado(res, preco, esperado, "BEMVINDO")


@pytest.mark.parametrize(
    "data_fora",
    [
        "0001-01-01",
        "2023-01-01",
        "2023-12-30",
        "2023-12-31",  # um dia antes do início
        "2025-01-01",  # um dia depois do fim
        "2025-06-15",
        "9999-12-31",
    ],
)
@pytest.mark.parametrize("preco", [0, 100, 1000])
def test_bemvindo_fora_da_janela_nao_aplica(data_fora, preco):
    res = aplicar_desconto(preco, "BEMVINDO", data_fora)
    _assert_resultado(res, preco, preco, None)


# ---------------------------------------------------------------------------
# NATAL: (preco * 85) // 100 em 24 ou 25 de dezembro de qualquer ano (1..9999)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "data_natal",
    [
        "0001-12-24",
        "0001-12-25",
        "1999-12-24",
        "2000-12-25",
        "2023-12-24",
        "2023-12-25",
        "2024-12-24",
        "2024-12-25",
        "2025-12-24",
        "2025-12-25",
        "9999-12-24",
        "9999-12-25",
    ],
)
def test_natal_em_24_e_25_de_dezembro_qualquer_ano(data_natal):
    res = aplicar_desconto(1000, "NATAL", data_natal)
    _assert_resultado(res, 1000, 850, "NATAL")


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),       # (1 * 85) // 100 = 0 (não 1 - 0 = 1)
        (6, 5),       # (6 * 85) // 100 = 5 (não 6 - 0 = 6)
        (10, 8),      # (10 * 85) // 100 = 8 (não 10 - 1 = 9)
        (11, 9),      # (11 * 85) // 100 = 9 (não 11 - 1 = 10)
        (100, 85),
        (101, 85),    # (101 * 85) // 100 = 85 (não 101 - 15 = 86)
        (10**16 + 3, ((10**16 + 3) * 85) // 100),  # precisão inteira vs float
    ],
)
@pytest.mark.parametrize("data_natal", ["2024-12-24", "2024-12-25"])
def test_natal_calculo_e_piso(preco, esperado, data_natal):
    res = aplicar_desconto(preco, "NATAL", data_natal)
    _assert_resultado(res, preco, esperado, "NATAL")


@pytest.mark.parametrize(
    "data_fora_natal",
    [
        "2024-12-01",
        "2024-12-23",  # um dia antes
        "2024-12-26",  # um dia depois
        "2024-12-31",
        "2024-01-24",  # mesmo dia em outro mês
        "2024-01-25",
        "2024-06-25",
        "2024-11-24",
        "2024-11-25",
        "0001-12-23",
        "9999-12-26",
    ],
)
@pytest.mark.parametrize("preco", [0, 100, 1000])
def test_natal_fora_da_janela_nao_aplica(data_fora_natal, preco):
    res = aplicar_desconto(preco, "NATAL", data_fora_natal)
    _assert_resultado(res, preco, preco, None)
