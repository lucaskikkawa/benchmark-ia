"""Suíte de testes para o módulo descontos."""

import os
import sys
from pathlib import Path
from datetime import date

_parent = str(Path(__file__).resolve().parent.parent)
if _parent not in sys.path:
    sys.path.insert(0, _parent)
_cwd = os.getcwd()
if _cwd not in sys.path:
    sys.path.insert(0, _cwd)

import pytest

from descontos import aplicar_desconto


# ============================================================================
# 1. Contrato do retorno
# ============================================================================

def _validar_contrato(resultado, preco_original):
    """Valida as restrições estritas do dicionário retornado."""
    assert isinstance(resultado, dict), "O retorno deve ser um dicionário"
    assert set(resultado.keys()) == {"preco_final", "desconto", "cupom_aplicado"}, (
        f"Chaves inválidas no dicionário: {set(resultado.keys())}"
    )
    preco_final = resultado["preco_final"]
    desconto = resultado["desconto"]
    cupom = resultado["cupom_aplicado"]

    assert isinstance(preco_final, int) and not isinstance(preco_final, bool), (
        "preco_final deve ser int (e não bool)"
    )
    assert isinstance(desconto, int) and not isinstance(desconto, bool), (
        "desconto deve ser int (e não bool)"
    )
    assert cupom is None or (isinstance(cupom, str) and not isinstance(cupom, bool)), (
        "cupom_aplicado deve ser str ou None"
    )
    assert preco_final >= 0, "preco_final não pode ser negativo"
    assert desconto >= 0, "desconto não pode ser negativo"
    assert preco_final + desconto == preco_original, (
        f"preco_final ({preco_final}) + desconto ({desconto}) != preco_original ({preco_original})"
    )
    assert desconto == preco_original - preco_final


def test_contrato_chaves_e_tipos():
    res = aplicar_desconto(1000, "OFF10", "2024-06-15")
    _validar_contrato(res, 1000)
    assert res == {
        "preco_final": 900,
        "desconto": 100,
        "cupom_aplicado": "OFF10",
    }


# ============================================================================
# 2. Validação do parâmetro `preco_centavos`
# ============================================================================

@pytest.mark.parametrize("preco_invalido", [
    True,
    False,
    100.0,
    0.0,
    -0.01,
    "100",
    "0",
    None,
    [100],
    (100,),
    {"preco": 100},
    object(),
])
def test_preco_centavos_tipo_invalido(preco_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(preco_invalido, "OFF10", "2024-06-15")


@pytest.mark.parametrize("preco_negativo", [-1, -2, -100, -500, -999999])
def test_preco_centavos_negativo(preco_negativo):
    with pytest.raises(ValueError):
        aplicar_desconto(preco_negativo, "OFF10", "2024-06-15")


def test_preco_centavos_zero():
    # Preço 0 é válido (int >= 0)
    for cupom, hoje, esperado_aplicado in [
        (None, "2024-06-15", None),
        ("", "2024-06-15", None),
        ("OFF10", "2024-06-15", "OFF10"),
        ("OFF5", "2024-06-15", "OFF5"),
        ("FIXO500", "2024-06-15", "FIXO500"),
        ("BEMVINDO", "2024-06-15", "BEMVINDO"),
        ("BEMVINDO", "2025-06-15", None),
        ("NATAL", "2024-12-25", "NATAL"),
        ("NATAL", "2024-12-26", None),
    ]:
        res = aplicar_desconto(0, cupom, hoje)
        _validar_contrato(res, 0)
        assert res["preco_final"] == 0
        assert res["desconto"] == 0
        assert res["cupom_aplicado"] == esperado_aplicado


# ============================================================================
# 3. Validação do parâmetro `cupom`
# ============================================================================

@pytest.mark.parametrize("cupom_tipo_invalido", [
    10,
    10.0,
    True,
    False,
    ["OFF10"],
    ("OFF10",),
    {"cupom": "OFF10"},
    object(),
])
def test_cupom_tipo_invalido(cupom_tipo_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom_tipo_invalido, "2024-06-15")


@pytest.mark.parametrize("cupom_desconhecido", [
    "DESCONTO",
    "OFF15",
    "PROMO",
    "XYZ",
    "OFF20",
    "FIXO100",
    "NATAL2024",
    "BEM-VINDO",
    "bem_vindo",
    "null",
    "None",
])
def test_cupom_desconhecido(cupom_desconhecido):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom_desconhecido, "2024-06-15")


@pytest.mark.parametrize("cupom_espacos_ou_case", [
    " OFF10",
    "OFF10 ",
    " OFF10 ",
    "off10",
    "Off10",
    "oFF10",
    " OFF5",
    "OFF5 ",
    "off5",
    "Off5",
    " FIXO500",
    "FIXO500 ",
    "fixo500",
    "Fixo500",
    " BEMVINDO",
    "BEMVINDO ",
    "bemvindo",
    "BemVindo",
    " NATAL",
    "NATAL ",
    "natal",
    "Natal",
])
def test_cupom_sem_strip_e_case_sensitive(cupom_espacos_ou_case):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom_espacos_ou_case, "2024-12-25")


@pytest.mark.parametrize("cupom_whitespace", [
    " ",
    "  ",
    "   ",
    "\t",
    "\n",
    "\r\n",
    " \t \n",
])
def test_cupom_espacos_em_branco(cupom_whitespace):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom_whitespace, "2024-06-15")


# ============================================================================
# 4. Validação do parâmetro `hoje`
# ============================================================================

@pytest.mark.parametrize("hoje_tipo_invalido", [
    None,
    123,
    20240101,
    True,
    False,
    date(2024, 6, 15),
    ["2024-06-15"],
    {"hoje": "2024-06-15"},
    object(),
])
def test_hoje_tipo_invalido(hoje_tipo_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, "OFF10", hoje_tipo_invalido)


@pytest.mark.parametrize("hoje_formato_invalido", [
    "",
    "2024",
    "2024-1-1",
    "2024-01-1",
    "2024-1-01",
    "2024-001-01",
    "2024/01/01",
    "2024.01.01",
    "20240101",
    "2024_01_01",
    "2024-01-01 ",
    " 2024-01-01",
    "2024-01-01T00:00:00",
    "YYYY-MM-DD",
    "abcd-ef-gh",
    "2024-aa-01",
    "2024-01-bb",
    "abcd-01-01",
    "2024-1-1000",
    "2024-01-01-01",
])
def test_hoje_formato_invalido(hoje_formato_invalido):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, "OFF10", hoje_formato_invalido)


@pytest.mark.parametrize("hoje_data_inexistente", [
    "2024-00-10",  # mês 0
    "2024-13-10",  # mês 13
    "2024-01-00",  # dia 0
    "2024-01-32",  # dia 32
    "2024-04-31",  # abril tem 30 dias
    "2024-06-31",  # junho tem 30 dias
    "2024-09-31",  # setembro tem 30 dias
    "2024-11-31",  # novembro tem 30 dias
    "2024-02-30",  # fevereiro nunca tem 30
    "2023-02-29",  # 2023 não é bissexto
    "1900-02-29",  # século não bissexto (múltiplo de 100, não de 400)
    "2100-02-29",  # século não bissexto
    "0000-12-25",  # ano 0 não é gregoriano 1..9999
    "10000-01-01", # ano 10000 fora do range
])
def test_hoje_data_inexistente_ou_fora_calendario(hoje_data_inexistente):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, "OFF10", hoje_data_inexistente)


@pytest.mark.parametrize("hoje_bissexto_e_limites", [
    "2000-02-29",  # ano bissexto por regra de 400
    "2024-02-29",  # ano bissexto padrão
    "0001-01-01",  # limite inferior gregoriano
    "0001-12-25",  # ano 1
    "9999-12-31",  # limite superior gregoriano
])
def test_hoje_datas_validas_limites(hoje_bissexto_e_limites):
    res = aplicar_desconto(1000, "OFF10", hoje_bissexto_e_limites)
    _validar_contrato(res, 1000)
    assert res["preco_final"] == 900
    assert res["desconto"] == 100
    assert res["cupom_aplicado"] == "OFF10"


# ============================================================================
# 5. Cupom `None` e `""` (sem desconto)
# ============================================================================

@pytest.mark.parametrize("cupom_vazio", [None, ""])
@pytest.mark.parametrize("preco", [0, 1, 99, 100, 500, 1000, 99999])
def test_cupom_none_ou_vazio_nao_altera_preco(cupom_vazio, preco):
    res = aplicar_desconto(preco, cupom_vazio, "2024-06-15")
    _validar_contrato(res, preco)
    assert res["preco_final"] == preco
    assert res["desconto"] == 0
    assert res["cupom_aplicado"] is None


# ============================================================================
# 6. Cupom `OFF10`
# ============================================================================

@pytest.mark.parametrize("preco, final_esperado, desconto_esperado", [
    (0, 0, 0),
    # Casos críticos onde (preco * 90) // 100 difere de preco - preco // 10:
    (1, 0, 1),    # 90//100 = 0 (desconto 1). Se preco - preco//10, seria 1 - 0 = 1 (desconto 0)
    (2, 1, 1),    # 180//100 = 1 (desconto 1)
    (9, 8, 1),    # 810//100 = 8 (desconto 1). Se preco - preco//10, seria 9 - 0 = 9 (desconto 0)
    (10, 9, 1),   # 900//100 = 9 (desconto 1)
    (11, 9, 2),   # 990//100 = 9 (desconto 2). Se preco - preco//10, seria 11 - 1 = 10 (desconto 1)
    (15, 13, 2),  # 1350//100 = 13 (desconto 2). Se preco - preco//10, seria 15 - 1 = 14 (desconto 1)
    (19, 17, 2),  # 1710//100 = 17 (desconto 2). Se preco - preco//10, seria 19 - 1 = 18 (desconto 1)
    (99, 89, 10), # 8910//100 = 89 (desconto 10). Se preco - preco//10, seria 99 - 9 = 90 (desconto 9)
    (100, 90, 10),
    (105, 94, 11), # 9450//100 = 94. Se preco - preco//10, seria 105 - 10 = 95
    (999, 899, 100),
    (1000, 900, 100),
])
def test_off10_calculo_e_arredondamento(preco, final_esperado, desconto_esperado):
    res = aplicar_desconto(preco, "OFF10", "2024-06-15")
    _validar_contrato(res, preco)
    assert res["preco_final"] == final_esperado
    assert res["desconto"] == desconto_esperado
    assert res["cupom_aplicado"] == "OFF10"
    # Garantia da fórmula exata do contrato:
    assert res["preco_final"] == (preco * 90) // 100


# ============================================================================
# 7. Cupom `OFF5`
# ============================================================================

@pytest.mark.parametrize("preco, final_esperado, desconto_esperado", [
    (0, 0, 0),
    # Casos críticos onde (preco * 95) // 100 difere de outras fórmulas:
    (1, 0, 1),     # 95//100 = 0 (desconto 1). Se preco - preco//20, seria 1 - 0 = 1 (desconto 0)
    (20, 19, 1),
    (21, 19, 2),   # 1995//100 = 19 (desconto 2). Se preco - preco//20, seria 21 - 1 = 20 (desconto 1)
    (100, 95, 5),
    (101, 95, 6),  # 9595//100 = 95 (desconto 6, explicitado no enunciado: 101 -> 95)
    (200, 190, 10),# 200 -> 190 (explicitado no enunciado)
    (201, 190, 11),# 19095//100 = 190
    (1000, 950, 50),
])
def test_off5_calculo_e_arredondamento(preco, final_esperado, desconto_esperado):
    res = aplicar_desconto(preco, "OFF5", "2024-06-15")
    _validar_contrato(res, preco)
    assert res["preco_final"] == final_esperado
    assert res["desconto"] == desconto_esperado
    assert res["cupom_aplicado"] == "OFF5"
    assert res["preco_final"] == (preco * 95) // 100


# ============================================================================
# 8. Cupom `FIXO500`
# ============================================================================

@pytest.mark.parametrize("preco, final_esperado, desconto_esperado", [
    (0, 0, 0),       # Piso 0, cupom aplicado
    (1, 0, 1),       # Piso 0, desconto 1
    (100, 0, 100),   # Preço 100 -> final 0 e desconto 100 (explicitado no enunciado)
    (499, 0, 499),   # Piso 0, desconto 499
    (500, 0, 500),   # Limite exato
    (501, 1, 500),   # Acima de 500
    (1000, 500, 500),
    (2500, 2000, 500),
])
def test_fixo500_calculo_e_piso_zero(preco, final_esperado, desconto_esperado):
    res = aplicar_desconto(preco, "FIXO500", "2024-06-15")
    _validar_contrato(res, preco)
    assert res["preco_final"] == final_esperado
    assert res["desconto"] == desconto_esperado
    assert res["cupom_aplicado"] == "FIXO500"
    assert res["preco_final"] == max(0, preco - 500)
    assert res["desconto"] == preco - res["preco_final"]


# ============================================================================
# 9. Cupom `BEMVINDO`
# ============================================================================

@pytest.mark.parametrize("hoje_dentro", [
    "2024-01-01",  # Extremo inicial inclusive
    "2024-01-02",
    "2024-02-29",  # Dia bissexto dentro da janela
    "2024-06-15",  # Meio do ano
    "2024-12-30",
    "2024-12-31",  # Extremo final inclusive
])
def test_bemvindo_dentro_da_janela(hoje_dentro):
    for preco in [0, 1, 6, 11, 100, 1000]:
        res = aplicar_desconto(preco, "BEMVINDO", hoje_dentro)
        _validar_contrato(res, preco)
        esperado_final = (preco * 80) // 100
        assert res["preco_final"] == esperado_final
        assert res["desconto"] == preco - esperado_final
        assert res["cupom_aplicado"] == "BEMVINDO"


@pytest.mark.parametrize("preco, final_esperado, desconto_esperado", [
    (0, 0, 0),
    # Diferença entre (preco * 80) // 100 e preco - (preco * 20) // 100:
    (1, 0, 1),    # 80//100 = 0 (desconto 1). Se preco - preco*20//100, seria 1 - 0 = 1 (desconto 0)
    (5, 4, 1),    # 400//100 = 4 (desconto 1)
    (6, 4, 2),    # 480//100 = 4 (desconto 2). Se preco - preco*20//100, seria 6 - 1 = 5 (desconto 1)
    (11, 8, 3),   # 880//100 = 8 (desconto 3). Se preco - preco*20//100, seria 11 - 2 = 9 (desconto 2)
    (100, 80, 20),
    (105, 84, 21),
    (1000, 800, 200),
])
def test_bemvindo_arredondamento_e_piso(preco, final_esperado, desconto_esperado):
    res = aplicar_desconto(preco, "BEMVINDO", "2024-06-15")
    _validar_contrato(res, preco)
    assert res["preco_final"] == final_esperado
    assert res["desconto"] == desconto_esperado
    assert res["cupom_aplicado"] == "BEMVINDO"
    assert res["preco_final"] == (preco * 80) // 100


@pytest.mark.parametrize("hoje_fora", [
    "2023-12-31",  # Véspera do início da janela
    "2023-01-01",  # Ano anterior
    "2025-01-01",  # Dia seguinte ao fim da janela
    "2025-12-31",  # Ano posterior
    "2020-05-10",
    "1999-06-15",
    "0001-01-01",
    "9999-12-31",
])
def test_bemvindo_fora_da_janela_nao_altera_preco(hoje_fora):
    for preco in [0, 1, 100, 1000]:
        res = aplicar_desconto(preco, "BEMVINDO", hoje_fora)
        _validar_contrato(res, preco)
        assert res["preco_final"] == preco
        assert res["desconto"] == 0
        assert res["cupom_aplicado"] is None


# ============================================================================
# 10. Cupom `NATAL`
# ============================================================================

@pytest.mark.parametrize("ano", ["2024", "2023", "2000", "1900", "0001", "9999"])
@pytest.mark.parametrize("dia", ["24", "25"])
def test_natal_datas_validas_qualquer_ano(ano, dia):
    hoje = f"{ano}-12-{dia}"
    for preco in [0, 1, 7, 13, 100, 1000]:
        res = aplicar_desconto(preco, "NATAL", hoje)
        _validar_contrato(res, preco)
        esperado_final = (preco * 85) // 100
        assert res["preco_final"] == esperado_final
        assert res["desconto"] == preco - esperado_final
        assert res["cupom_aplicado"] == "NATAL"


@pytest.mark.parametrize("preco, final_esperado, desconto_esperado", [
    (0, 0, 0),
    # Diferença entre (preco * 85) // 100 e preco - (preco * 15) // 100:
    (1, 0, 1),    # Preço 1 em 25/12 -> final 0 (explicitado no enunciado)
    (6, 5, 1),    # 510//100 = 5 (desconto 1)
    (7, 5, 2),    # 595//100 = 5 (desconto 2). Se preco - preco*15//100, seria 7 - 1 = 6 (desconto 1)
    (13, 11, 2),  # 1105//100 = 11 (desconto 2). Se preco - preco*15//100, seria 13 - 1 = 12 (desconto 1)
    (100, 85, 15),
    (1000, 850, 150),
])
def test_natal_arredondamento_e_piso(preco, final_esperado, desconto_esperado):
    res = aplicar_desconto(preco, "NATAL", "2024-12-25")
    _validar_contrato(res, preco)
    assert res["preco_final"] == final_esperado
    assert res["desconto"] == desconto_esperado
    assert res["cupom_aplicado"] == "NATAL"
    assert res["preco_final"] == (preco * 85) // 100


@pytest.mark.parametrize("hoje_fora_natal", [
    "2024-12-23",  # Véspera de 24
    "2024-12-26",  # Dia seguinte a 25
    "2024-12-01",
    "2024-11-24",  # Mesmo dia, outro mês
    "2024-11-25",
    "2024-01-24",
    "2024-01-25",
    "2024-06-15",
    "2023-12-23",
    "0001-12-23",
    "9999-12-26",
])
def test_natal_fora_da_data_nao_altera_preco(hoje_fora_natal):
    for preco in [0, 1, 100, 1000]:
        res = aplicar_desconto(preco, "NATAL", hoje_fora_natal)
        _validar_contrato(res, preco)
        assert res["preco_final"] == preco
        assert res["desconto"] == 0
        assert res["cupom_aplicado"] is None
