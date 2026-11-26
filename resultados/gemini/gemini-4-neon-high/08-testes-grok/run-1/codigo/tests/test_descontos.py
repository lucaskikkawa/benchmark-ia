"""Suíte de testes para o módulo descontos."""

from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
import sys
import pytest

for _caminho in (str(Path.cwd()), str(Path(__file__).resolve().parent.parent)):
    if _caminho not in sys.path:
        sys.path.append(_caminho)

from descontos import aplicar_desconto


CHAVES_ESPERADAS = {"preco_final", "desconto", "cupom_aplicado"}


def _verificar_resultado(res, preco_centavos, preco_final_esperado, cupom_esperado):
    assert type(res) is dict
    assert set(res.keys()) == CHAVES_ESPERADAS
    assert type(res["preco_final"]) is int
    assert type(res["desconto"]) is int
    assert res["preco_final"] == preco_final_esperado
    assert res["desconto"] == preco_centavos - preco_final_esperado
    if cupom_esperado is None:
        assert res["cupom_aplicado"] is None
    else:
        assert type(res["cupom_aplicado"]) is str
        assert res["cupom_aplicado"] == cupom_esperado


# ---------------------------------------------------------------------------
# Contrato geral: estrutura do dict, argumentos nomeados, pureza
# ---------------------------------------------------------------------------


def test_contrato_chaves_exatas_e_argumentos_nomeados():
    res = aplicar_desconto(
        preco_centavos=1000,
        cupom="OFF10",
        hoje="2024-06-15",
    )
    _verificar_resultado(res, 1000, 900, "OFF10")


def test_mutacao_do_retorno_nao_afeta_chamadas_seguintes():
    res1 = aplicar_desconto(1000, "OFF10", "2024-06-15")
    res1["preco_final"] = -999
    res1["extra"] = True
    res2 = aplicar_desconto(1000, "OFF10", "2024-06-15")
    _verificar_resultado(res2, 1000, 900, "OFF10")


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
        float("-inf"),
        float("nan"),
        "100",
        "0",
        b"100",
        None,
        Decimal("100"),
        [100],
        {"preco": 100},
        complex(100, 0),
    ],
)
@pytest.mark.parametrize("cupom", [None, "OFF10"])
def test_preco_tipo_invalido_levanta_type_error(preco_invalido, cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(preco_invalido, cupom, "2024-06-15")


@pytest.mark.parametrize("preco_negativo", [-1, -2, -100, -500, -10**9])
@pytest.mark.parametrize(
    "cupom", [None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL"]
)
def test_preco_negativo_levanta_value_error(preco_negativo, cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(preco_negativo, cupom, "2024-12-25")


# ---------------------------------------------------------------------------
# Validação de cupom
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cupom_tipo_invalido",
    [
        0,
        1,
        10.0,
        False,
        True,
        b"",
        b"OFF10",
        [],
        ["OFF10"],
        {},
        (),
        object(),
    ],
)
def test_cupom_tipo_invalido_levanta_type_error(cupom_tipo_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom_tipo_invalido, "2024-06-15")


@pytest.mark.parametrize(
    "cupom_invalido",
    [
        " ",
        "   ",
        "\t",
        "\n",
        "\r\n",
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
        "OFF1",
        "OFF15",
        "OFF20",
        "OFF50",
        "OFF100",
        "FIXO100",
        "FIXO50",
        "FIXO5000",
        "BEM-VINDO",
        "BEM_VINDO",
        "NATAL2024",
        "NATAL25",
        "NONE",
        "None",
        "null",
        "DESCONTO",
        "OFF10\x00",
        "OFF1O",
        "FIXO5OO",
    ],
)
@pytest.mark.parametrize("preco", [0, 1000])
def test_cupom_desconhecido_ou_mal_formatado_levanta_value_error(cupom_invalido, preco):
    with pytest.raises(ValueError):
        aplicar_desconto(preco, cupom_invalido, "2024-12-25")


@pytest.mark.parametrize("cupom_sem_desconto", [None, ""])
@pytest.mark.parametrize("preco", [0, 1, 100, 999, 10000])
def test_cupom_none_ou_vazio_nao_aplica_desconto(cupom_sem_desconto, preco):
    res = aplicar_desconto(preco, cupom_sem_desconto, "2024-12-25")
    _verificar_resultado(res, preco, preco, None)


# ---------------------------------------------------------------------------
# Validação de hoje (tipo, formato e calendário gregoriano)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hoje_tipo_invalido",
    [
        None,
        date(2024, 6, 15),
        datetime(2024, 6, 15, 0, 0),
        20240615,
        2024.06,
        b"2024-06-15",
        ["2024-06-15"],
        True,
        False,
    ],
)
@pytest.mark.parametrize("cupom", [None, "", "OFF10", "BEMVINDO", "NATAL"])
def test_hoje_tipo_invalido_levanta_type_error(hoje_tipo_invalido, cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom, hoje_tipo_invalido)


@pytest.mark.parametrize(
    "data_invalida",
    [
        "",
        " ",
        "2024",
        "2024-01",
        "20240101",
        "2024-1-01",
        "2024-01-1",
        "2024-1-1",
        "24-01-01",
        "01-01-2024",
        "2024/01/01",
        "2024-01/01",
        "2024/01-01",
        "2024.01.01",
        " 2024-01-01",
        "2024-01-01 ",
        "2024-01-01\n",
        "2024-01-01T00:00:00",
        "2024-W01-1",
        "+2024-01-01",
        "-001-01-01",
        "10000-01-01",
        "abcd-ef-gh",
        "2024-ab-01",
        "2024-01-ab",
        "2024--1-01",
        "2024-01--1",
        # Ano 0 não existe em datetime.date
        "0000-01-01",
        "0000-02-29",
        # Meses e dias fora do intervalo
        "2024-00-10",
        "2024-13-01",
        "2024-01-00",
        "2024-01-32",
        "2024-12-32",
        "2024-02-30",
        "2024-02-31",
        "2024-04-31",
        "2024-06-31",
        "2024-09-31",
        "2024-11-31",
        # 29 de fevereiro em anos não bissextos
        "2023-02-29",
        "2025-02-29",
        "2021-02-29",
        "0001-02-29",
        "9999-02-29",
        # Regra do século: divisível por 100 mas não por 400 não é bissexto
        "1900-02-29",
        "2100-02-29",
        "1800-02-29",
        "2200-02-29",
        "0100-02-29",
    ],
)
@pytest.mark.parametrize("cupom", [None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL"])
def test_hoje_data_invalida_levanta_value_error(data_invalida, cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom, data_invalida)


@pytest.mark.parametrize("cupom", [None, "", "OFF10", "FIXO500", "BEMVINDO", "NATAL"])
def test_preco_zero_ainda_valida_data_e_tipo_hoje(cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(0, cupom, "2023-02-29")
    with pytest.raises(TypeError):
        aplicar_desconto(0, cupom, date(2024, 6, 15))


@pytest.mark.parametrize(
    "data_valida",
    [
        "0001-01-01",
        "0001-12-25",
        "0004-02-29",
        "1600-02-29",
        "1900-02-28",
        "2000-02-29",
        "2020-02-29",
        "2023-02-28",
        "2024-02-29",
        "2400-02-29",
        "2024-01-31",
        "2024-03-31",
        "2024-04-30",
        "2024-05-31",
        "2024-06-30",
        "2024-07-31",
        "2024-08-31",
        "2024-09-30",
        "2024-10-31",
        "2024-11-30",
        "2024-12-31",
        "9999-12-31",
    ],
)
def test_hoje_datas_gregorianas_validas_aceitas(data_valida):
    res = aplicar_desconto(1000, "OFF10", data_valida)
    _verificar_resultado(res, 1000, 900, "OFF10")


# ---------------------------------------------------------------------------
# Cupom OFF10: (preco * 90) // 100
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (2, 1),
        (5, 4),
        (9, 8),
        (10, 9),
        (11, 9),
        (15, 13),
        (19, 17),
        (50, 45),
        (99, 89),
        (100, 90),
        (101, 90),
        (199, 179),
        (200, 180),
        (999, 899),
        (1000, 900),
        (10**18 + 37, ((10**18 + 37) * 90) // 100),
    ],
)
def test_off10_calculo_com_piso(preco, esperado):
    res = aplicar_desconto(preco, "OFF10", "2025-07-04")
    _verificar_resultado(res, preco, esperado, "OFF10")


@pytest.mark.parametrize(
    "hoje", ["0001-01-01", "2023-12-31", "2024-06-15", "2024-12-25", "2025-01-01", "9999-12-31"]
)
def test_off10_independe_da_data(hoje):
    res = aplicar_desconto(101, "OFF10", hoje)
    _verificar_resultado(res, 101, 90, "OFF10")


# ---------------------------------------------------------------------------
# Cupom OFF5: (preco * 95) // 100
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (2, 1),
        (10, 9),
        (19, 18),
        (20, 19),
        (21, 19),
        (30, 28),
        (50, 47),
        (99, 94),
        (100, 95),
        (101, 95),
        (199, 189),
        (200, 190),
        (999, 949),
        (1000, 950),
        (10**18 + 37, ((10**18 + 37) * 95) // 100),
    ],
)
def test_off5_calculo_com_piso(preco, esperado):
    res = aplicar_desconto(preco, "OFF5", "2025-07-04")
    _verificar_resultado(res, preco, esperado, "OFF5")


@pytest.mark.parametrize(
    "hoje", ["0001-01-01", "2023-12-31", "2024-06-15", "2024-12-25", "2025-01-01", "9999-12-31"]
)
def test_off5_independe_da_data(hoje):
    res = aplicar_desconto(101, "OFF5", hoje)
    _verificar_resultado(res, 101, 95, "OFF5")


# ---------------------------------------------------------------------------
# Cupom FIXO500: max(0, preco - 500)
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
        (50000, 49500),
        (10**18 + 37, 10**18 + 37 - 500),
    ],
)
def test_fixo500_com_piso_zero(preco, esperado):
    res = aplicar_desconto(preco, "FIXO500", "2025-07-04")
    _verificar_resultado(res, preco, esperado, "FIXO500")


@pytest.mark.parametrize(
    "hoje", ["0001-01-01", "2023-12-31", "2024-06-15", "2024-12-25", "2025-01-01", "9999-12-31"]
)
def test_fixo500_independe_da_data(hoje):
    res = aplicar_desconto(750, "FIXO500", hoje)
    _verificar_resultado(res, 750, 250, "FIXO500")


# ---------------------------------------------------------------------------
# Cupom BEMVINDO: (preco * 80) // 100 em 2024-01-01 .. 2024-12-31 (inclusive)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (2, 1),
        (4, 3),
        (5, 4),
        (6, 4),
        (99, 79),
        (100, 80),
        (101, 80),
        (1000, 800),
        (10**18 + 37, ((10**18 + 37) * 80) // 100),
    ],
)
def test_bemvindo_calculo_dentro_da_janela(preco, esperado):
    res = aplicar_desconto(preco, "BEMVINDO", "2024-06-15")
    _verificar_resultado(res, preco, esperado, "BEMVINDO")


@pytest.mark.parametrize(
    "hoje",
    [
        "2024-01-01",
        "2024-01-02",
        "2024-02-29",
        "2024-06-15",
        "2024-12-24",
        "2024-12-25",
        "2024-12-30",
        "2024-12-31",
    ],
)
def test_bemvindo_ativo_nos_extremos_e_meio_de_2024(hoje):
    res = aplicar_desconto(101, "BEMVINDO", hoje)
    _verificar_resultado(res, 101, 80, "BEMVINDO")


@pytest.mark.parametrize(
    "hoje",
    [
        "0001-01-01",
        "2023-01-01",
        "2023-06-15",
        "2023-12-31",
        "2025-01-01",
        "2025-06-15",
        "2025-12-31",
        "9999-12-31",
    ],
)
@pytest.mark.parametrize("preco", [0, 1, 1000])
def test_bemvindo_fora_da_janela_nao_altera_preco(hoje, preco):
    res = aplicar_desconto(preco, "BEMVINDO", hoje)
    _verificar_resultado(res, preco, preco, None)


# ---------------------------------------------------------------------------
# Cupom NATAL: (preco * 85) // 100 em 24 ou 25 de dezembro de qualquer ano
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("hoje", ["2024-12-24", "2024-12-25"])
@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (2, 1),
        (6, 5),
        (7, 5),
        (10, 8),
        (20, 17),
        (30, 25),
        (99, 84),
        (100, 85),
        (101, 85),
        (1000, 850),
        (10**18 + 37, ((10**18 + 37) * 85) // 100),
    ],
)
def test_natal_calculo_em_24_e_25_de_dezembro(hoje, preco, esperado):
    res = aplicar_desconto(preco, "NATAL", hoje)
    _verificar_resultado(res, preco, esperado, "NATAL")


@pytest.mark.parametrize(
    "hoje",
    [
        "0001-12-24",
        "0001-12-25",
        "1900-12-24",
        "1900-12-25",
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
def test_natal_ativo_em_qualquer_ano_valido(hoje):
    res = aplicar_desconto(101, "NATAL", hoje)
    _verificar_resultado(res, 101, 85, "NATAL")


@pytest.mark.parametrize(
    "hoje",
    [
        "0001-12-23",
        "0001-12-26",
        "2023-12-23",
        "2023-12-26",
        "2024-12-01",
        "2024-12-12",
        "2024-12-23",
        "2024-12-26",
        "2024-12-31",
        "2024-01-24",
        "2024-01-25",
        "2024-06-24",
        "2024-06-25",
        "2024-11-24",
        "2024-11-25",
        "9999-12-23",
        "9999-12-26",
    ],
)
@pytest.mark.parametrize("preco", [0, 1, 1000])
def test_natal_fora_de_24_e_25_de_dezembro_nao_altera_preco(hoje, preco):
    res = aplicar_desconto(preco, "NATAL", hoje)
    _verificar_resultado(res, preco, preco, None)
