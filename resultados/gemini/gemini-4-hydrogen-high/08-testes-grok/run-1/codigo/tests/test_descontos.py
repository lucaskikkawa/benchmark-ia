from datetime import date
from pathlib import Path
import sys

import pytest

_ROOT = str(Path(__file__).resolve().parent.parent)
if _ROOT not in sys.path:
    sys.path.append(_ROOT)

from descontos import aplicar_desconto


def _assert_resultado(res, preco_inicial, preco_final_esperado, cupom_esperado):
    assert type(res) is dict
    assert set(res.keys()) == {"preco_final", "desconto", "cupom_aplicado"}
    assert type(res["preco_final"]) is int
    assert type(res["desconto"]) is int
    assert res["preco_final"] == preco_final_esperado
    assert res["desconto"] == preco_inicial - preco_final_esperado
    assert res["cupom_aplicado"] == cupom_esperado
    if cupom_esperado is None:
        assert res["cupom_aplicado"] is None
    else:
        assert type(res["cupom_aplicado"]) is str


# --- Validação de tipos e limites de preco_centavos ---


@pytest.mark.parametrize("preco_invalido", [True, False, 0.0, 100.0, 10.5, "100", None, [], {}])
def test_preco_tipo_invalido(preco_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(preco_invalido, "OFF10", "2024-06-15")


@pytest.mark.parametrize("preco_negativo", [-1, -100, -500, -10**12])
@pytest.mark.parametrize("cupom", [None, "", "OFF10", "FIXO500", "BEMVINDO", "NATAL"])
def test_preco_negativo(preco_negativo, cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(preco_negativo, cupom, "2024-12-25")


# --- Validação de cupom ---


@pytest.mark.parametrize("cupom_invalido", [10, 0, True, False, 1.5, b"OFF10", ["OFF10"], {}])
def test_cupom_tipo_invalido(cupom_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom_invalido, "2024-06-15")


@pytest.mark.parametrize("cupom", [None, ""])
@pytest.mark.parametrize("hoje", ["2024-06-15", "2024-12-25", "2023-01-01"])
@pytest.mark.parametrize("preco", [0, 1, 1000])
def test_cupom_none_ou_vazio_sem_desconto(cupom, hoje, preco):
    res = aplicar_desconto(preco, cupom, hoje)
    _assert_resultado(res, preco, preco, None)


@pytest.mark.parametrize(
    "cupom_desconhecido",
    [
        " ",
        "\t",
        "\n",
        " OFF10",
        "OFF10 ",
        "off10",
        "Off10",
        "off5",
        "fixo500",
        "bemvindo",
        "natal",
        "OFF20",
        "OFF15",
        "FIXO",
        "FIXO100",
        "BEMVINDO2024",
        "NATAL25",
        "CUPOM",
    ],
)
def test_cupom_desconhecido_ou_com_espacos_ou_caixa_errada(cupom_desconhecido):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom_desconhecido, "2024-12-25")


# --- Validação de hoje ---


@pytest.mark.parametrize(
    "hoje_invalido",
    [date(2024, 6, 15), None, 20240615, b"2024-06-15", True, False, 2024.06, []],
)
def test_hoje_tipo_invalido(hoje_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, "OFF10", hoje_invalido)


@pytest.mark.parametrize(
    "data_invalida",
    [
        "",
        "20240615",
        "2024-6-15",
        "2024-06-5",
        "24-06-15",
        "2024/06/15",
        "2024.06.15",
        " 2024-06-15",
        "2024-06-15 ",
        "2024-06-15T00:00:00",
        "+2024-06-1",
        "abcd-ef-gh",
        "0000-01-01",
        "2024-00-01",
        "2024-13-01",
        "2024-01-00",
        "2024-01-32",
        "2024-04-31",
        "2024-06-31",
        "2024-02-30",
        "2023-02-29",
        "1900-02-29",
        "2100-02-29",
    ],
)
@pytest.mark.parametrize("cupom", [None, "", "OFF10"])
def test_hoje_invalido_levanta_value_error(data_invalida, cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom, data_invalida)


@pytest.mark.parametrize(
    "data_valida",
    ["0001-01-01", "0001-12-25", "2000-02-29", "2024-02-29", "9999-12-31"],
)
def test_hoje_datas_validas_extremas_e_bissextos(data_valida):
    res = aplicar_desconto(100, None, data_valida)
    _assert_resultado(res, 100, 100, None)


# --- Cupom OFF10 ---


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (9, 8),
        (10, 9),
        (15, 13),
        (19, 17),
        (99, 89),
        (100, 90),
        (105, 94),
        (1000, 900),
        (10**18 + 3, ((10**18 + 3) * 90) // 100),
    ],
)
@pytest.mark.parametrize("hoje", ["2023-05-10", "2024-06-15", "2025-12-25"])
def test_off10(preco, esperado, hoje):
    res = aplicar_desconto(preco, "OFF10", hoje)
    _assert_resultado(res, preco, esperado, "OFF10")


# --- Cupom OFF5 ---


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (19, 18),
        (20, 19),
        (101, 95),
        (200, 190),
        (1000, 950),
        (10**18 + 3, ((10**18 + 3) * 95) // 100),
    ],
)
@pytest.mark.parametrize("hoje", ["2023-05-10", "2024-06-15", "2025-12-25"])
def test_off5(preco, esperado, hoje):
    res = aplicar_desconto(preco, "OFF5", hoje)
    _assert_resultado(res, preco, esperado, "OFF5")


# --- Cupom FIXO500 ---


@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (100, 0),
        (499, 0),
        (500, 0),
        (501, 1),
        (1500, 1000),
        (10**18 + 500, 10**18),
    ],
)
@pytest.mark.parametrize("hoje", ["2023-05-10", "2024-06-15", "2025-12-25"])
def test_fixo500(preco, esperado, hoje):
    res = aplicar_desconto(preco, "FIXO500", hoje)
    _assert_resultado(res, preco, esperado, "FIXO500")


# --- Cupom BEMVINDO ---


@pytest.mark.parametrize(
    "hoje",
    ["2024-01-01", "2024-02-29", "2024-06-15", "2024-12-25", "2024-12-31"],
)
@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (4, 3),
        (5, 4),
        (102, 81),
        (1000, 800),
        (10**18 + 3, ((10**18 + 3) * 80) // 100),
    ],
)
def test_bemvindo_dentro_da_janela(hoje, preco, esperado):
    res = aplicar_desconto(preco, "BEMVINDO", hoje)
    _assert_resultado(res, preco, esperado, "BEMVINDO")


@pytest.mark.parametrize(
    "hoje",
    ["0001-01-01", "2023-01-01", "2023-12-31", "2025-01-01", "2025-12-25", "9999-12-31"],
)
@pytest.mark.parametrize("preco", [0, 1, 1000])
def test_bemvindo_fora_da_janela(hoje, preco):
    res = aplicar_desconto(preco, "BEMVINDO", hoje)
    _assert_resultado(res, preco, preco, None)


# --- Cupom NATAL ---


@pytest.mark.parametrize(
    "hoje",
    [
        "0001-12-24",
        "0001-12-25",
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
@pytest.mark.parametrize(
    "preco, esperado",
    [
        (0, 0),
        (1, 0),
        (6, 5),
        (20, 17),
        (105, 89),
        (1000, 850),
        (10**18 + 3, ((10**18 + 3) * 85) // 100),
    ],
)
def test_natal_dias_validos(hoje, preco, esperado):
    res = aplicar_desconto(preco, "NATAL", hoje)
    _assert_resultado(res, preco, esperado, "NATAL")


@pytest.mark.parametrize(
    "hoje",
    [
        "0001-12-23",
        "2024-12-01",
        "2024-12-23",
        "2024-12-26",
        "2024-11-24",
        "2024-11-25",
        "2024-01-24",
        "2024-01-25",
        "9999-12-26",
    ],
)
@pytest.mark.parametrize("preco", [0, 1, 1000])
def test_natal_outros_dias(hoje, preco):
    res = aplicar_desconto(preco, "NATAL", hoje)
    _assert_resultado(res, preco, preco, None)
