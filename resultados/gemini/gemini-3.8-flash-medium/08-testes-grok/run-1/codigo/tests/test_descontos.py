"""Testes para o módulo descontos."""

import sys
from pathlib import Path
from datetime import date
import pytest

# Garante que descontos.py na raiz seja importável em qualquer forma de execução do pytest
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from descontos import aplicar_desconto


def _validar_resultado(resultado, preco_original, esperado_final, esperado_desconto, esperado_cupom):
    """Verifica contrato estrito do retorno de aplicar_desconto."""
    assert isinstance(resultado, dict), "Retorno deve ser dict"
    assert set(resultado.keys()) == {"preco_final", "desconto", "cupom_aplicado"}, (
        f"Chaves inválidas no dicionário: {set(resultado.keys())}"
    )
    assert len(resultado) == 3

    final = resultado["preco_final"]
    desconto = resultado["desconto"]
    cupom = resultado["cupom_aplicado"]

    assert type(final) is int and not isinstance(final, bool), "preco_final deve ser int estrito"
    assert type(desconto) is int and not isinstance(desconto, bool), "desconto deve ser int estrito"
    assert cupom == esperado_cupom, f"cupom_aplicado esperado {esperado_cupom!r}, obteve {cupom!r}"
    assert final == esperado_final, f"preco_final esperado {esperado_final}, obteve {final}"
    assert desconto == esperado_desconto, f"desconto esperado {esperado_desconto}, obteve {desconto}"
    assert desconto == preco_original - final, "desconto deve ser exatamente preco_original - preco_final"


# ---------------------------------------------------------------------------
# Validação de preco_centavos
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco_invalido",
    [
        True,
        False,
        100.0,
        0.0,
        1.5,
        "100",
        "0",
        None,
        [],
        [100],
        {},
        {"preco": 100},
        (100,),
        object(),
    ],
)
def test_preco_centavos_tipo_invalido(preco_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(preco_invalido, "OFF10", "2024-06-01")


@pytest.mark.parametrize("preco_negativo", [-1, -2, -10, -100, -500, -999999])
def test_preco_centavos_negativo(preco_negativo):
    with pytest.raises(ValueError):
        aplicar_desconto(preco_negativo, "OFF10", "2024-06-01")


def test_preco_centavos_zero_valido():
    # Preço zero é int >= 0 válido para todos os casos
    res_none = aplicar_desconto(0, None, "2024-06-01")
    _validar_resultado(res_none, 0, 0, 0, None)

    res_vazio = aplicar_desconto(0, "", "2024-06-01")
    _validar_resultado(res_vazio, 0, 0, 0, None)

    res_off10 = aplicar_desconto(0, "OFF10", "2024-06-01")
    _validar_resultado(res_off10, 0, 0, 0, "OFF10")

    res_off5 = aplicar_desconto(0, "OFF5", "2024-06-01")
    _validar_resultado(res_off5, 0, 0, 0, "OFF5")

    res_fixo = aplicar_desconto(0, "FIXO500", "2024-06-01")
    _validar_resultado(res_fixo, 0, 0, 0, "FIXO500")

    res_bemvindo_dentro = aplicar_desconto(0, "BEMVINDO", "2024-06-01")
    _validar_resultado(res_bemvindo_dentro, 0, 0, 0, "BEMVINDO")

    res_bemvindo_fora = aplicar_desconto(0, "BEMVINDO", "2023-06-01")
    _validar_resultado(res_bemvindo_fora, 0, 0, 0, None)

    res_natal_dentro = aplicar_desconto(0, "NATAL", "2024-12-25")
    _validar_resultado(res_natal_dentro, 0, 0, 0, "NATAL")

    res_natal_fora = aplicar_desconto(0, "NATAL", "2024-12-20")
    _validar_resultado(res_natal_fora, 0, 0, 0, None)


# ---------------------------------------------------------------------------
# Validação de cupom
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cupom_tipo_invalido",
    [
        123,
        0,
        10.5,
        0.0,
        True,
        False,
        [],
        ["OFF10"],
        {},
        {"cupom": "OFF10"},
        (1,),
        object(),
    ],
)
def test_cupom_tipo_invalido(cupom_tipo_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(100, cupom_tipo_invalido, "2024-06-01")


@pytest.mark.parametrize(
    "cupom_desconhecido",
    [
        "INVALID",
        "OFF20",
        "OFF",
        "FIXO",
        "FIXO100",
        "PROMO",
        "DESCONTO",
        "CUPOM",
        "123",
        "NATAL2024",
    ],
)
def test_cupom_desconhecido(cupom_desconhecido):
    with pytest.raises(ValueError):
        aplicar_desconto(100, cupom_desconhecido, "2024-06-01")


@pytest.mark.parametrize(
    "cupom_case",
    [
        "off10",
        "Off10",
        "oFF10",
        "off5",
        "Off5",
        "fixo500",
        "Fixo500",
        "bemvindo",
        "Bemvindo",
        "BemVindo",
        "natal",
        "Natal",
    ],
)
def test_cupom_case_sensitive(cupom_case):
    # Sem case-folding
    with pytest.raises(ValueError):
        aplicar_desconto(100, cupom_case, "2024-12-25")


@pytest.mark.parametrize(
    "cupom_com_espaco",
    [
        " OFF10",
        "OFF10 ",
        " OFF10 ",
        "\tOFF10",
        "OFF10\t",
        "OFF10\n",
        " OFF5",
        "OFF5 ",
        " FIXO500",
        "FIXO500 ",
        " BEMVINDO",
        "BEMVINDO ",
        " NATAL",
        "NATAL ",
    ],
)
def test_cupom_sem_strip(cupom_com_espaco):
    # Não há strip: espaços antes ou depois tornam código desconhecido
    with pytest.raises(ValueError):
        aplicar_desconto(100, cupom_com_espaco, "2024-12-25")


@pytest.mark.parametrize(
    "espacos",
    [
        " ",
        "  ",
        "\t",
        "\n",
        " \t ",
        "\r\n",
    ],
)
def test_cupom_espacos_nao_sao_vazio(espacos):
    # " " e "\t" não são vazio: são texto desconhecido e levantam ValueError
    with pytest.raises(ValueError):
        aplicar_desconto(100, espacos, "2024-06-01")


# ---------------------------------------------------------------------------
# Validação de hoje
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "hoje_tipo_invalido",
    [
        date(2024, 6, 1),
        20240601,
        123,
        None,
        True,
        False,
        ["2024-06-01"],
        {"hoje": "2024-06-01"},
        (2024, 6, 1),
        object(),
    ],
)
def test_hoje_tipo_invalido(hoje_tipo_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(100, "OFF10", hoje_tipo_invalido)


@pytest.mark.parametrize(
    "hoje_formato_invalido",
    [
        "",
        "2024/06/01",
        "2024.06.01",
        "2024_06_01",
        "2024-6-1",
        "2024-06-1",
        "2024-6-01",
        "24-06-01",
        "2024-06-001",
        "20240601",
        "2024-06-010",
        " 2024-06-01",
        "2024-06-01 ",
        "\t2024-06-01",
        "2024-06-01\n",
        "2024-W01-1",
        "2024-001",
        "+2024-06-01",
        "2024-xx-yy",
        "abcd-ef-gh",
        "2024-1a-01",
        "2024-06-1b",
    ],
)
def test_hoje_formato_invalido(hoje_formato_invalido):
    with pytest.raises(ValueError):
        aplicar_desconto(100, "OFF10", hoje_formato_invalido)


@pytest.mark.parametrize(
    "data_inexistente",
    [
        # Regra do século para ano bissexto
        "1900-02-29",
        "2100-02-29",
        "2200-02-29",
        "2300-02-29",
        # Ano não-bissexto comum
        "2023-02-29",
        "2021-02-29",
        # Fevereiro dias > 29
        "2024-02-30",
        "2024-02-31",
        # Meses de 30 dias com 31
        "2024-04-31",
        "2024-06-31",
        "2024-09-31",
        "2024-11-31",
        # Mês inválido
        "2024-00-15",
        "2024-13-01",
        # Dia inválido
        "2024-01-00",
        "2024-01-32",
        # Limites gregorianos de datetime.date (1 a 9999)
        "0000-01-01",
        "0000-12-31",
        "-001-01-01",
    ],
)
def test_hoje_data_inexistente_gregoriano(data_inexistente):
    with pytest.raises(ValueError):
        aplicar_desconto(100, "OFF10", data_inexistente)


@pytest.mark.parametrize(
    "data_valida",
    [
        "2000-02-29",  # Ano 2000 é bissexto (múltiplo de 400)
        "2024-02-29",  # Ano bissexto comum
        "0001-01-01",  # Limite inferior gregoriano
        "0001-12-25",
        "9999-12-31",  # Limite superior gregoriano
    ],
)
def test_hoje_datas_validas_casos_limite(data_valida):
    res = aplicar_desconto(100, "OFF10", data_valida)
    _validar_resultado(res, 100, 90, 10, "OFF10")


# ---------------------------------------------------------------------------
# Comportamento de cupom None e ""
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("preco", [0, 1, 50, 100, 499, 500, 1000])
def test_cupom_none(preco):
    res = aplicar_desconto(preco, None, "2024-06-01")
    _validar_resultado(res, preco, preco, 0, None)


@pytest.mark.parametrize("preco", [0, 1, 50, 100, 499, 500, 1000])
def test_cupom_vazio(preco):
    res = aplicar_desconto(preco, "", "2024-06-01")
    _validar_resultado(res, preco, preco, 0, None)


# ---------------------------------------------------------------------------
# Cupom OFF10: (preco * 90) // 100
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco,esperado_final,esperado_desconto",
    [
        (0, 0, 0),
        (1, 0, 1),
        (2, 1, 1),
        (9, 8, 1),
        (10, 9, 1),
        (11, 9, 2),
        (19, 17, 2),
        (20, 18, 2),
        (99, 89, 10),
        (100, 90, 10),
        (101, 90, 11),
        (109, 98, 11),
        (110, 99, 11),
        (1000, 900, 100),
        (12345, 11110, 1235),
    ],
)
def test_off10_valores_especificos(preco, esperado_final, esperado_desconto):
    res = aplicar_desconto(preco, "OFF10", "2024-06-01")
    _validar_resultado(res, preco, esperado_final, esperado_desconto, "OFF10")


def test_off10_varredura():
    for preco in range(501):
        esperado_final = (preco * 90) // 100
        esperado_desconto = preco - esperado_final
        res = aplicar_desconto(preco, "OFF10", "2024-06-01")
        _validar_resultado(res, preco, esperado_final, esperado_desconto, "OFF10")


# ---------------------------------------------------------------------------
# Cupom OFF5: (preco * 95) // 100
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco,esperado_final,esperado_desconto",
    [
        (0, 0, 0),
        (1, 0, 1),
        (2, 1, 1),
        (19, 18, 1),
        (20, 19, 1),
        (21, 19, 2),
        (100, 95, 5),
        (101, 95, 6),  # Exemplo do enunciado: 101 -> 95
        (200, 190, 10),  # Exemplo do enunciado: 200 -> 190
        (1000, 950, 50),
    ],
)
def test_off5_valores_especificos(preco, esperado_final, esperado_desconto):
    res = aplicar_desconto(preco, "OFF5", "2024-06-01")
    _validar_resultado(res, preco, esperado_final, esperado_desconto, "OFF5")


def test_off5_varredura():
    for preco in range(501):
        esperado_final = (preco * 95) // 100
        esperado_desconto = preco - esperado_final
        res = aplicar_desconto(preco, "OFF5", "2024-06-01")
        _validar_resultado(res, preco, esperado_final, esperado_desconto, "OFF5")


# ---------------------------------------------------------------------------
# Cupom FIXO500: max(0, preco - 500)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "preco,esperado_final,esperado_desconto",
    [
        (0, 0, 0),  # Exemplo enunciado: Preço 0 continua 0 e conta como aplicado
        (1, 0, 1),
        (100, 0, 100),  # Exemplo enunciado: Preço 100 -> final 0 e desconto 100
        (499, 0, 499),
        (500, 0, 500),
        (501, 1, 500),
        (999, 499, 500),
        (1000, 500, 500),
        (1500, 1000, 500),
    ],
)
def test_fixo500_valores_especificos(preco, esperado_final, esperado_desconto):
    res = aplicar_desconto(preco, "FIXO500", "2024-06-01")
    _validar_resultado(res, preco, esperado_final, esperado_desconto, "FIXO500")


def test_fixo500_varredura():
    for preco in range(1001):
        esperado_final = max(0, preco - 500)
        esperado_desconto = preco - esperado_final
        res = aplicar_desconto(preco, "FIXO500", "2024-06-01")
        _validar_resultado(res, preco, esperado_final, esperado_desconto, "FIXO500")


# ---------------------------------------------------------------------------
# Cupom BEMVINDO: (preco * 80) // 100 entre 2024-01-01 e 2024-12-31 inclusive
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "data_valida",
    [
        "2024-01-01",  # Extremo inicial (inclusive)
        "2024-01-02",
        "2024-02-29",  # Ano bissexto
        "2024-06-15",
        "2024-12-30",
        "2024-12-31",  # Extremo final (inclusive)
    ],
)
def test_bemvindo_dentro_da_janela(data_valida):
    # Preço 100 -> final 80, desconto 20
    res = aplicar_desconto(100, "BEMVINDO", data_valida)
    _validar_resultado(res, 100, 80, 20, "BEMVINDO")


@pytest.mark.parametrize(
    "data_invalida",
    [
        "2023-12-31",  # Um dia antes da janela
        "2025-01-01",  # Um dia depois da janela
        "2023-01-01",
        "2023-06-15",
        "2025-06-15",
        "2025-12-31",
        "1999-05-10",
        "0001-06-01",
        "9999-06-01",
    ],
)
def test_bemvindo_fora_da_janela(data_invalida):
    # Fora da janela: não é erro, preço não muda e cupom_aplicado fica None
    res = aplicar_desconto(100, "BEMVINDO", data_invalida)
    _validar_resultado(res, 100, 100, 0, None)

    # Preço zero fora da janela
    res_zero = aplicar_desconto(0, "BEMVINDO", data_invalida)
    _validar_resultado(res_zero, 0, 0, 0, None)


@pytest.mark.parametrize(
    "preco,esperado_final,esperado_desconto",
    [
        (0, 0, 0),
        (1, 0, 1),
        (4, 3, 1),
        (5, 4, 1),
        (6, 4, 2),
        (100, 80, 20),
        (101, 80, 21),
        (1000, 800, 200),
    ],
)
def test_bemvindo_formula_valores(preco, esperado_final, esperado_desconto):
    res = aplicar_desconto(preco, "BEMVINDO", "2024-06-01")
    _validar_resultado(res, preco, esperado_final, esperado_desconto, "BEMVINDO")


def test_bemvindo_varredura():
    for preco in range(501):
        esperado_final = (preco * 80) // 100
        esperado_desconto = preco - esperado_final
        res = aplicar_desconto(preco, "BEMVINDO", "2024-07-01")
        _validar_resultado(res, preco, esperado_final, esperado_desconto, "BEMVINDO")


# ---------------------------------------------------------------------------
# Cupom NATAL: (preco * 85) // 100 somente em 24 ou 25 de dezembro (ano 1 a 9999)
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "data_natal",
    [
        "2024-12-24",
        "2024-12-25",
        "2023-12-24",
        "2023-12-25",
        "2025-12-24",
        "2025-12-25",
        "0001-12-24",
        "0001-12-25",
        "1999-12-24",
        "1999-12-25",
        "9999-12-24",
        "9999-12-25",
    ],
)
def test_natal_dentro_da_janela(data_natal):
    res = aplicar_desconto(100, "NATAL", data_natal)
    _validar_resultado(res, 100, 85, 15, "NATAL")


@pytest.mark.parametrize(
    "data_nao_natal",
    [
        "2024-12-23",  # Véspera da véspera
        "2024-12-26",  # Dia seguinte ao Natal
        "2024-11-24",  # Mesmo dia, mês anterior
        "2024-11-25",
        "2024-01-24",
        "2024-01-25",
        "2024-06-24",
        "2024-06-25",
        "2024-12-01",
        "2024-12-31",
        "2023-12-23",
        "2023-12-26",
    ],
)
def test_natal_fora_da_janela(data_nao_natal):
    # Fora da janela: não é erro, preço não muda e cupom_aplicado fica None
    res = aplicar_desconto(100, "NATAL", data_nao_natal)
    _validar_resultado(res, 100, 100, 0, None)

    res_zero = aplicar_desconto(0, "NATAL", data_nao_natal)
    _validar_resultado(res_zero, 0, 0, 0, None)


@pytest.mark.parametrize(
    "preco,esperado_final,esperado_desconto",
    [
        (0, 0, 0),
        (1, 0, 1),  # Exemplo enunciado: Preço 1 em 25/12 -> final 0
        (6, 5, 1),
        (7, 5, 2),
        (13, 11, 2),
        (100, 85, 15),
        (101, 85, 16),
        (1000, 850, 150),
    ],
)
def test_natal_formula_valores(preco, esperado_final, esperado_desconto):
    res_24 = aplicar_desconto(preco, "NATAL", "2024-12-24")
    _validar_resultado(res_24, preco, esperado_final, esperado_desconto, "NATAL")

    res_25 = aplicar_desconto(preco, "NATAL", "2024-12-25")
    _validar_resultado(res_25, preco, esperado_final, esperado_desconto, "NATAL")


def test_natal_varredura():
    for preco in range(501):
        esperado_final = (preco * 85) // 100
        esperado_desconto = preco - esperado_final
        res = aplicar_desconto(preco, "NATAL", "2024-12-25")
        _validar_resultado(res, preco, esperado_final, esperado_desconto, "NATAL")
