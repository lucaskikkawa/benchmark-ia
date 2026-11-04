"""Suíte de testes para o módulo descontos.py."""

import sys
from pathlib import Path

# Assegura que o diretório do projeto esteja acessível mesmo se invocado via `pytest` diretamente
_root = str(Path(__file__).resolve().parent.parent)
if _root not in sys.path:
    sys.path.insert(0, _root)

import pytest
from descontos import aplicar_desconto


# ==============================================================================
# 1. CONTRATO DO RETORNO (TIPO, CHAVES E INVARIANTES)
# ==============================================================================

def test_retorno_formato_chaves_e_tipos():
    res = aplicar_desconto(100, "OFF10", "2024-06-15")
    assert isinstance(res, dict)
    assert set(res.keys()) == {"preco_final", "desconto", "cupom_aplicado"}
    assert len(res) == 3
    assert type(res["preco_final"]) is int
    assert type(res["desconto"]) is int
    assert isinstance(res["cupom_aplicado"], str)
    assert res["preco_final"] == 90
    assert res["desconto"] == 10
    assert res["cupom_aplicado"] == "OFF10"


def test_retorno_quando_nenhum_cupom_aplicado():
    res = aplicar_desconto(100, None, "2024-06-15")
    assert isinstance(res, dict)
    assert set(res.keys()) == {"preco_final", "desconto", "cupom_aplicado"}
    assert len(res) == 3
    assert type(res["preco_final"]) is int
    assert type(res["desconto"]) is int
    assert res["preco_final"] == 100
    assert res["desconto"] == 0
    assert res["cupom_aplicado"] is None


def test_invariante_desconto_igual_preco_menos_final():
    for preco in [0, 1, 10, 100, 499, 500, 501, 1000]:
        for cupom in [None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL"]:
            res = aplicar_desconto(preco, cupom, "2024-12-25")
            assert res["desconto"] == preco - res["preco_final"]
            assert res["preco_final"] >= 0
            assert res["desconto"] >= 0


# ==============================================================================
# 2. VALIDAÇÃO DO PARÂMETRO preco_centavos
# ==============================================================================

@pytest.mark.parametrize("invalido", [
    True,
    False,
    100.0,
    0.0,
    -0.0,
    10.5,
    "100",
    None,
    [100],
    (100,),
    {"preco": 100},
    object(),
])
def test_preco_centavos_tipo_invalido(invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(invalido, "OFF10", "2024-06-15")


@pytest.mark.parametrize("negativo", [-1, -2, -100, -500, -100000])
def test_preco_centavos_negativo(negativo):
    with pytest.raises(ValueError):
        aplicar_desconto(negativo, "OFF10", "2024-06-15")


def test_preco_centavos_zero_todos_cupons():
    # Preço 0 deve ser aceito e retornar 0 para tudo, com o cupom marcado como aplicado se válido
    res_off10 = aplicar_desconto(0, "OFF10", "2024-06-15")
    assert res_off10 == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "OFF10"}

    res_off5 = aplicar_desconto(0, "OFF5", "2024-06-15")
    assert res_off5 == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "OFF5"}

    res_fixo = aplicar_desconto(0, "FIXO500", "2024-06-15")
    assert res_fixo == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "FIXO500"}

    res_bv = aplicar_desconto(0, "BEMVINDO", "2024-06-15")
    assert res_bv == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "BEMVINDO"}

    res_natal = aplicar_desconto(0, "NATAL", "2024-12-25")
    assert res_natal == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "NATAL"}

    res_none = aplicar_desconto(0, None, "2024-06-15")
    assert res_none == {"preco_final": 0, "desconto": 0, "cupom_aplicado": None}

    res_vazio = aplicar_desconto(0, "", "2024-06-15")
    assert res_vazio == {"preco_final": 0, "desconto": 0, "cupom_aplicado": None}


# ==============================================================================
# 3. VALIDAÇÃO DO PARÂMETRO cupom
# ==============================================================================

@pytest.mark.parametrize("tipo_invalido", [
    123,
    0,
    True,
    False,
    10.5,
    [],
    {},
    object(),
])
def test_cupom_tipo_invalido(tipo_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(100, tipo_invalido, "2024-06-15")


@pytest.mark.parametrize("desconhecido", [
    " ",
    "   ",
    "\t",
    "\n",
    "\r\n",
    " OFF10",
    "OFF10 ",
    " OFF10 ",
    "\tOFF10",
    "off10",
    "Off10",
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
    "DESCONTO",
    "OFF20",
    "FIXO100",
    "XYZ",
    "123",
])
def test_cupom_desconhecido_ou_com_espacos(desconhecido):
    with pytest.raises(ValueError):
        aplicar_desconto(100, desconhecido, "2024-06-15")


@pytest.mark.parametrize("sem_cupom", [None, ""])
def test_cupom_none_ou_vazio(sem_cupom):
    res = aplicar_desconto(1500, sem_cupom, "2024-06-15")
    assert res == {"preco_final": 1500, "desconto": 0, "cupom_aplicado": None}


# ==============================================================================
# 4. VALIDAÇÃO DO PARÂMETRO hoje
# ==============================================================================

@pytest.mark.parametrize("hoje_tipo_invalido", [
    123,
    None,
    True,
    False,
    [],
    {},
    object(),
])
def test_hoje_tipo_invalido(hoje_tipo_invalido):
    with pytest.raises(TypeError):
        aplicar_desconto(100, "OFF10", hoje_tipo_invalido)


@pytest.mark.parametrize("hoje_formato_invalido", [
    "",
    "2024",
    "2024-1",
    "2024-1-1",
    "2024-01-1",
    "2024-1-01",
    "24-01-01",
    "2024/01/01",
    "2024.01.01",
    "2024_01_01",
    "20240101",
    "2024-W01-1",
    "2024-01-01 ",
    " 2024-01-01",
    "2024-01-01\n",
    "2024-001-01",
    "2024-01-001",
    "10000-01-01",
    "-001-01-01",
    "+2024-01-01",
    "abcd-ef-gh",
    "2024-ab-01",
    "2024-01-cd",
])
def test_hoje_formato_invalido(hoje_formato_invalido):
    with pytest.raises(ValueError):
        aplicar_desconto(100, "OFF10", hoje_formato_invalido)


@pytest.mark.parametrize("hoje_calendario_invalido", [
    "1900-02-29",  # Século não bissexto
    "2100-02-29",  # Século não bissexto
    "2023-02-29",  # Não bissexto
    "2024-02-30",  # Fevereiro não tem 30
    "2024-02-31",  # Fevereiro não tem 31
    "2024-04-31",  # Abril tem 30 dias
    "2024-06-31",  # Junho tem 30 dias
    "2024-09-31",  # Setembro tem 30 dias
    "2024-11-31",  # Novembro tem 30 dias
    "2024-00-10",  # Mês 0
    "2024-13-01",  # Mês 13
    "2024-01-00",  # Dia 0
    "2024-01-32",  # Dia 32
    "0000-01-01",  # Ano 0 não existe no calendário gregoriano do datetime.date
])
def test_hoje_calendario_invalido(hoje_calendario_invalido):
    with pytest.raises(ValueError):
        aplicar_desconto(100, "OFF10", hoje_calendario_invalido)


@pytest.mark.parametrize("hoje_valido", [
    "2000-02-29",  # Século bissexto (divisível por 400)
    "2024-02-29",  # Ano bissexto
    "0001-12-25",  # Ano 1
    "9999-12-31",  # Ano 9999
])
def test_hoje_extremos_validos(hoje_valido):
    res = aplicar_desconto(1000, "OFF10", hoje_valido)
    assert res == {"preco_final": 900, "desconto": 100, "cupom_aplicado": "OFF10"}


# ==============================================================================
# 5. CUPOM OFF10
# ==============================================================================

@pytest.mark.parametrize("preco,esperado_final,esperado_desc", [
    (0, 0, 0),
    (1, 0, 1),       # (1 * 90) // 100 = 0 (não é 1 - 1 // 10)
    (2, 1, 1),       # (2 * 90) // 100 = 1
    (9, 8, 1),       # (9 * 90) // 100 = 8
    (10, 9, 1),      # (10 * 90) // 100 = 9
    (11, 9, 2),      # (11 * 90) // 100 = 9 (não é 11 - 1 = 10)
    (15, 13, 2),     # (15 * 90) // 100 = 13 (não é 15 - 1 = 14)
    (19, 17, 2),     # (19 * 90) // 100 = 17 (não é 19 - 1 = 18)
    (99, 89, 10),    # (99 * 90) // 100 = 89 (não é 99 - 9 = 90)
    (100, 90, 10),   # 100 * 90 // 100 = 90
    (105, 94, 11),   # 105 * 90 // 100 = 9450 // 100 = 94
    (999, 899, 100), # 999 * 90 // 100 = 899
    (1000, 900, 100),
])
def test_cupom_off10_calculo_e_piso(preco, esperado_final, esperado_desc):
    res = aplicar_desconto(preco, "OFF10", "2024-06-15")
    assert res["preco_final"] == esperado_final
    assert res["desconto"] == esperado_desc
    assert res["cupom_aplicado"] == "OFF10"


# ==============================================================================
# 6. CUPOM OFF5
# ==============================================================================

@pytest.mark.parametrize("preco,esperado_final,esperado_desc", [
    (0, 0, 0),
    (1, 0, 1),       # (1 * 95) // 100 = 0 (não é 1 - 0 = 1)
    (19, 18, 1),     # (19 * 95) // 100 = 18
    (20, 19, 1),     # (20 * 95) // 100 = 19
    (21, 19, 2),     # (21 * 95) // 100 = 19 (não é 21 - 1 = 20)
    (100, 95, 5),
    (101, 95, 6),    # Exemplo do enunciado: 101 -> 95
    (200, 190, 10),  # Exemplo do enunciado: 200 -> 190
    (1000, 950, 50),
])
def test_cupom_off5_calculo_e_piso(preco, esperado_final, esperado_desc):
    res = aplicar_desconto(preco, "OFF5", "2024-06-15")
    assert res["preco_final"] == esperado_final
    assert res["desconto"] == esperado_desc
    assert res["cupom_aplicado"] == "OFF5"


# ==============================================================================
# 7. CUPOM FIXO500
# ==============================================================================

@pytest.mark.parametrize("preco,esperado_final,esperado_desc", [
    (0, 0, 0),         # Preço 0 continua 0 e conta como aplicado
    (1, 0, 1),
    (100, 0, 100),     # Exemplo do enunciado: 100 -> final 0 e desconto 100
    (499, 0, 499),
    (500, 0, 500),
    (501, 1, 500),
    (600, 100, 500),
    (1000, 500, 500),
    (10000, 9500, 500),
])
def test_cupom_fixo500_calculo_e_piso(preco, esperado_final, esperado_desc):
    res = aplicar_desconto(preco, "FIXO500", "2024-06-15")
    assert res["preco_final"] == esperado_final
    assert res["desconto"] == esperado_desc
    assert res["cupom_aplicado"] == "FIXO500"


# ==============================================================================
# 8. CUPOM BEMVINDO
# ==============================================================================

@pytest.mark.parametrize("hoje_dentro", [
    "2024-01-01",  # Extremo inicial (inclusive)
    "2024-01-02",
    "2024-02-29",  # Ano bissexto dentro da janela
    "2024-06-15",
    "2024-12-30",
    "2024-12-31",  # Extremo final (inclusive)
])
def test_cupom_bemvindo_dentro_da_janela(hoje_dentro):
    res = aplicar_desconto(100, "BEMVINDO", hoje_dentro)
    assert res == {"preco_final": 80, "desconto": 20, "cupom_aplicado": "BEMVINDO"}


@pytest.mark.parametrize("preco,esperado_final,esperado_desc", [
    (0, 0, 0),
    (1, 0, 1),     # (1 * 80) // 100 = 0 (não é 1 - (1 * 20)//100 = 1)
    (6, 4, 2),     # (6 * 80) // 100 = 4 (não é 6 - 1 = 5)
    (10, 8, 2),
    (100, 80, 20),
    (1000, 800, 200),
])
def test_cupom_bemvindo_calculo_e_piso(preco, esperado_final, esperado_desc):
    res = aplicar_desconto(preco, "BEMVINDO", "2024-06-15")
    assert res["preco_final"] == esperado_final
    assert res["desconto"] == esperado_desc
    assert res["cupom_aplicado"] == "BEMVINDO"


@pytest.mark.parametrize("hoje_fora", [
    "2023-12-31",  # Véspera do início
    "2025-01-01",  # Dia seguinte ao fim
    "2023-01-01",
    "2023-06-15",
    "2025-12-31",
    "2026-05-10",
    "0001-06-15",
    "9999-06-15",
])
def test_cupom_bemvindo_fora_da_janela(hoje_fora):
    res = aplicar_desconto(500, "BEMVINDO", hoje_fora)
    assert res == {"preco_final": 500, "desconto": 0, "cupom_aplicado": None}


def test_cupom_bemvindo_fora_da_janela_preco_zero():
    res = aplicar_desconto(0, "BEMVINDO", "2023-12-31")
    assert res == {"preco_final": 0, "desconto": 0, "cupom_aplicado": None}


# ==============================================================================
# 9. CUPOM NATAL
# ==============================================================================

@pytest.mark.parametrize("hoje_natal", [
    "2024-12-24",
    "2024-12-25",
    "2023-12-24",
    "2023-12-25",
    "0001-12-24",
    "0001-12-25",
    "2000-12-24",
    "2000-12-25",
    "9999-12-24",
    "9999-12-25",
])
def test_cupom_natal_dias_validos_em_varios_anos(hoje_natal):
    res = aplicar_desconto(100, "NATAL", hoje_natal)
    assert res == {"preco_final": 85, "desconto": 15, "cupom_aplicado": "NATAL"}


@pytest.mark.parametrize("preco,esperado_final,esperado_desc", [
    (0, 0, 0),
    (1, 0, 1),     # Exemplo do enunciado: Preço 1 em 25/12 -> final 0
    (7, 5, 2),     # (7 * 85) // 100 = 5 (não é 7 - (7 * 15)//100 = 6)
    (100, 85, 15),
    (1000, 850, 150),
])
def test_cupom_natal_calculo_e_piso(preco, esperado_final, esperado_desc):
    res = aplicar_desconto(preco, "NATAL", "2024-12-25")
    assert res["preco_final"] == esperado_final
    assert res["desconto"] == esperado_desc
    assert res["cupom_aplicado"] == "NATAL"


@pytest.mark.parametrize("hoje_fora_natal", [
    "2024-12-23",  # Véspera da véspera
    "2024-12-26",  # Boxing Day
    "2024-11-24",  # Mês anterior
    "2024-11-25",
    "2024-01-24",
    "2024-01-25",
    "2024-07-15",
    "2024-12-01",
    "2024-12-31",
    "0001-12-23",
    "9999-12-26",
])
def test_cupom_natal_fora_dos_dias(hoje_fora_natal):
    res = aplicar_desconto(500, "NATAL", hoje_fora_natal)
    assert res == {"preco_final": 500, "desconto": 0, "cupom_aplicado": None}


def test_cupom_natal_fora_dos_dias_preco_zero():
    res = aplicar_desconto(0, "NATAL", "2024-12-23")
    assert res == {"preco_final": 0, "desconto": 0, "cupom_aplicado": None}
