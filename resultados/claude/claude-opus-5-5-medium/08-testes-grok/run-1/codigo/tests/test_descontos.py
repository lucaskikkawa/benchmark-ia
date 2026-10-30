import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from descontos import aplicar_desconto  # noqa: E402

DIA_COMUM = "2023-06-15"
PRECOS = list(range(0, 1201)) + [9999, 10000, 10001, 123456789, 10**20 + 7]


def checar(r, preco, final, cupom):
    assert isinstance(r, dict)
    assert set(r.keys()) == {"preco_final", "desconto", "cupom_aplicado"}
    assert len(r) == 3
    assert type(r["preco_final"]) is int
    assert type(r["desconto"]) is int
    assert r["preco_final"] == final
    assert r["desconto"] == preco - final
    assert r["desconto"] >= 0
    assert r["preco_final"] >= 0
    if cupom is None:
        assert r["cupom_aplicado"] is None
    else:
        assert type(r["cupom_aplicado"]) is str
        assert r["cupom_aplicado"] == cupom


# ---------- sem cupom ----------

@pytest.mark.parametrize("cupom", [None, ""])
@pytest.mark.parametrize("preco", [0, 1, 99, 100, 500, 501, 12345])
@pytest.mark.parametrize("hoje", [DIA_COMUM, "2024-06-01", "2024-12-25", "0001-01-01", "9999-12-31"])
def test_sem_cupom(cupom, preco, hoje):
    checar(aplicar_desconto(preco, cupom, hoje), preco, preco, None)


# ---------- percentuais ----------

def test_off10_todos_precos():
    for p in PRECOS:
        checar(aplicar_desconto(p, "OFF10", DIA_COMUM), p, (p * 90) // 100, "OFF10")


def test_off10_exemplos():
    checar(aplicar_desconto(1, "OFF10", DIA_COMUM), 1, 0, "OFF10")
    checar(aplicar_desconto(0, "OFF10", DIA_COMUM), 0, 0, "OFF10")
    checar(aplicar_desconto(19, "OFF10", DIA_COMUM), 19, 17, "OFF10")  # 19 - 19//10 = 18
    checar(aplicar_desconto(100, "OFF10", DIA_COMUM), 100, 90, "OFF10")
    checar(aplicar_desconto(9, "OFF10", DIA_COMUM), 9, 8, "OFF10")


def test_off5_todos_precos():
    for p in PRECOS:
        checar(aplicar_desconto(p, "OFF5", DIA_COMUM), p, (p * 95) // 100, "OFF5")


def test_off5_exemplos():
    checar(aplicar_desconto(200, "OFF5", DIA_COMUM), 200, 190, "OFF5")
    checar(aplicar_desconto(101, "OFF5", DIA_COMUM), 101, 95, "OFF5")
    checar(aplicar_desconto(1, "OFF5", DIA_COMUM), 1, 0, "OFF5")
    checar(aplicar_desconto(19, "OFF5", DIA_COMUM), 19, 18, "OFF5")
    checar(aplicar_desconto(0, "OFF5", DIA_COMUM), 0, 0, "OFF5")


@pytest.mark.parametrize("cupom", ["OFF10", "OFF5", "FIXO500"])
@pytest.mark.parametrize("hoje", ["0001-01-01", "2024-01-01", "2024-12-25", "2025-03-03", "9999-12-31"])
def test_cupons_sem_janela_valem_em_qualquer_data(cupom, hoje):
    r = aplicar_desconto(1000, cupom, hoje)
    esperado = {"OFF10": 900, "OFF5": 950, "FIXO500": 500}[cupom]
    checar(r, 1000, esperado, cupom)


# ---------- FIXO500 ----------

def test_fixo500_todos_precos():
    for p in PRECOS:
        checar(aplicar_desconto(p, "FIXO500", DIA_COMUM), p, max(0, p - 500), "FIXO500")


@pytest.mark.parametrize("preco,final", [(0, 0), (1, 0), (100, 0), (499, 0), (500, 0),
                                         (501, 1), (600, 100), (1000, 500)])
def test_fixo500_piso(preco, final):
    checar(aplicar_desconto(preco, "FIXO500", DIA_COMUM), preco, final, "FIXO500")


def test_fixo500_preco_100():
    r = aplicar_desconto(100, "FIXO500", DIA_COMUM)
    assert r == {"preco_final": 0, "desconto": 100, "cupom_aplicado": "FIXO500"}


def test_fixo500_preco_zero_aplicado():
    r = aplicar_desconto(0, "FIXO500", DIA_COMUM)
    assert r == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "FIXO500"}


# ---------- BEMVINDO ----------

DENTRO_2024 = ["2024-01-01", "2024-01-02", "2024-02-29", "2024-06-15", "2024-12-24",
               "2024-12-25", "2024-12-30", "2024-12-31"]
FORA_2024 = ["2023-12-31", "2025-01-01", "2023-01-01", "2025-12-31", "2023-06-15",
             "0001-01-01", "9999-12-31", "2014-06-15", "2034-06-15", "2124-06-15"]


@pytest.mark.parametrize("hoje", DENTRO_2024)
def test_bemvindo_dentro(hoje):
    for p in PRECOS:
        checar(aplicar_desconto(p, "BEMVINDO", hoje), p, (p * 80) // 100, "BEMVINDO")


@pytest.mark.parametrize("hoje", FORA_2024)
@pytest.mark.parametrize("preco", [0, 1, 4, 5, 100, 999, 12345])
def test_bemvindo_fora(hoje, preco):
    checar(aplicar_desconto(preco, "BEMVINDO", hoje), preco, preco, None)


def test_bemvindo_extremos_exatos():
    assert aplicar_desconto(1000, "BEMVINDO", "2024-01-01") == {
        "preco_final": 800, "desconto": 200, "cupom_aplicado": "BEMVINDO"}
    assert aplicar_desconto(1000, "BEMVINDO", "2024-12-31") == {
        "preco_final": 800, "desconto": 200, "cupom_aplicado": "BEMVINDO"}
    assert aplicar_desconto(1000, "BEMVINDO", "2023-12-31") == {
        "preco_final": 1000, "desconto": 0, "cupom_aplicado": None}
    assert aplicar_desconto(1000, "BEMVINDO", "2025-01-01") == {
        "preco_final": 1000, "desconto": 0, "cupom_aplicado": None}


def test_bemvindo_conta():
    # 9*80//100 = 7 ; 9 - 9*20//100 = 8
    checar(aplicar_desconto(9, "BEMVINDO", "2024-05-05"), 9, 7, "BEMVINDO")
    checar(aplicar_desconto(1, "BEMVINDO", "2024-05-05"), 1, 0, "BEMVINDO")
    checar(aplicar_desconto(0, "BEMVINDO", "2024-05-05"), 0, 0, "BEMVINDO")


# ---------- NATAL ----------

NATAL_DIAS = ["2024-12-24", "2024-12-25", "2023-12-24", "2023-12-25", "0001-12-24",
              "0001-12-25", "9999-12-24", "9999-12-25", "1900-12-25", "2100-12-24"]
NAO_NATAL = ["2024-12-23", "2024-12-26", "2023-12-23", "2023-12-26", "2024-11-24",
             "2024-11-25", "2024-01-24", "2024-01-25", "2024-12-01", "2024-12-31",
             "2024-10-25", "2024-02-24", "0001-01-01", "9999-12-31", "2024-06-15",
             "2024-12-14", "2024-12-15", "2024-12-04", "2024-12-05", "2024-02-12"]


@pytest.mark.parametrize("hoje", NATAL_DIAS)
def test_natal_dentro(hoje):
    for p in PRECOS:
        checar(aplicar_desconto(p, "NATAL", hoje), p, (p * 85) // 100, "NATAL")


@pytest.mark.parametrize("hoje", NAO_NATAL)
@pytest.mark.parametrize("preco", [0, 1, 6, 7, 100, 999, 12345])
def test_natal_fora(hoje, preco):
    checar(aplicar_desconto(preco, "NATAL", hoje), preco, preco, None)


def test_natal_exemplos():
    assert aplicar_desconto(1, "NATAL", "2024-12-25") == {
        "preco_final": 0, "desconto": 1, "cupom_aplicado": "NATAL"}
    # 7*85//100 = 5 ; 7 - 7*15//100 = 6
    checar(aplicar_desconto(7, "NATAL", "2022-12-24"), 7, 5, "NATAL")
    checar(aplicar_desconto(100, "NATAL", "2022-12-24"), 100, 85, "NATAL")
    checar(aplicar_desconto(0, "NATAL", "2022-12-25"), 0, 0, "NATAL")


# ---------- erros de tipo ----------

@pytest.mark.parametrize("preco", [True, False, 1.0, 0.0, 100.5, "100", None, [100], 10**0 * 1.0])
def test_preco_tipo_invalido(preco):
    with pytest.raises(TypeError):
        aplicar_desconto(preco, None, DIA_COMUM)
    with pytest.raises(TypeError):
        aplicar_desconto(preco, "OFF10", DIA_COMUM)


@pytest.mark.parametrize("preco", [-1, -2, -100, -500, -10**12])
def test_preco_negativo(preco):
    for cupom in [None, "", "OFF10", "OFF5", "FIXO500"]:
        with pytest.raises(ValueError):
            aplicar_desconto(preco, cupom, DIA_COMUM)
    with pytest.raises(ValueError):
        aplicar_desconto(preco, "BEMVINDO", "2024-05-05")
    with pytest.raises(ValueError):
        aplicar_desconto(preco, "NATAL", "2024-12-25")


def test_preco_negativo_nao_e_typeerror():
    try:
        aplicar_desconto(-1, None, DIA_COMUM)
    except TypeError:
        pytest.fail("negativo deveria ser ValueError")
    except ValueError:
        pass
    else:
        pytest.fail("sem erro")


@pytest.mark.parametrize("cupom", [1, 0, 10, 1.5, b"OFF10", ["OFF10"], True, False, object()])
def test_cupom_tipo_invalido(cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom, DIA_COMUM)


@pytest.mark.parametrize("hoje", [None, 20240101, 2024.0, b"2024-01-01", ["2024-01-01"], True])
def test_hoje_tipo_invalido(hoje):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, None, hoje)
    with pytest.raises(TypeError):
        aplicar_desconto(1000, "OFF10", hoje)


def test_hoje_date_objeto_e_typeerror():
    from datetime import date, datetime
    with pytest.raises(TypeError):
        aplicar_desconto(1000, None, date(2024, 1, 1))
    with pytest.raises(TypeError):
        aplicar_desconto(1000, "BEMVINDO", datetime(2024, 1, 1))


# ---------- cupom desconhecido ----------

@pytest.mark.parametrize("cupom", [" ", "\t", "\n", "  ", " OFF10", "OFF10 ", "off10", "Off10",
                                   "OFF", "OFF1", "OFF100", "OFF15", "OFF20", "FIXO", "FIXO50",
                                   "FIXO5000", "fixo500", "bemvindo", "Bemvindo", "BEMVINDO ",
                                   " NATAL", "natal", "Natal", "XYZ", "DESCONTO", "None", "0",
                                   "OFF 10", "OFF5 ", "OFF05", "\tNATAL", "BEM VINDO"])
def test_cupom_desconhecido(cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom, DIA_COMUM)
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom, "2024-12-25")
    with pytest.raises(ValueError):
        aplicar_desconto(0, cupom, "2024-06-01")


# ---------- datas ----------

@pytest.mark.parametrize("hoje", ["2000-02-29", "0001-12-25", "0001-01-01", "9999-12-31",
                                  "2024-02-29", "1600-02-29", "2400-02-29", "1996-02-29",
                                  "2023-02-28", "1900-02-28", "2100-02-28", "2023-01-31",
                                  "2023-03-31", "2023-04-30", "2023-12-31", "0004-02-29"])
def test_datas_validas(hoje):
    checar(aplicar_desconto(1000, None, hoje), 1000, 1000, None)
    checar(aplicar_desconto(1000, "OFF10", hoje), 1000, 900, "OFF10")


@pytest.mark.parametrize("hoje", ["1900-02-29", "2100-02-29", "2023-02-29", "2200-02-29",
                                  "2019-02-29", "0001-02-29", "1800-02-29", "2023-02-30",
                                  "2024-02-30", "2023-04-31", "2023-06-31", "2023-09-31",
                                  "2023-11-31", "2023-13-01", "2023-00-10", "2023-01-00",
                                  "2023-01-32", "0000-01-01", "0000-12-25", "2024-12-32",
                                  "", "2024-1-01", "2024-01-1", "24-01-01", "2024/01/01",
                                  "01-01-2024", "2024-01-01 ", " 2024-01-01", "20240101",
                                  "2024-01-01T00:00", "abcd-ef-gh", "2024_01_01", "hoje",
                                  "2024-12-24x", "2024-02-31"])
def test_datas_invalidas(hoje):
    for cupom in [None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL"]:
        with pytest.raises(ValueError):
            aplicar_desconto(1000, cupom, hoje)


# ---------- ordem/combinações ----------

def test_resultado_novo_dict_e_sem_efeito_colateral():
    r1 = aplicar_desconto(1000, "OFF10", DIA_COMUM)
    r1["preco_final"] = -5
    r2 = aplicar_desconto(1000, "OFF10", DIA_COMUM)
    assert r2 == {"preco_final": 900, "desconto": 100, "cupom_aplicado": "OFF10"}


def test_cupons_independentes():
    hoje = "2024-12-25"
    assert aplicar_desconto(1000, "OFF10", hoje)["preco_final"] == 900
    assert aplicar_desconto(1000, "OFF5", hoje)["preco_final"] == 950
    assert aplicar_desconto(1000, "FIXO500", hoje)["preco_final"] == 500
    assert aplicar_desconto(1000, "BEMVINDO", hoje)["preco_final"] == 800
    assert aplicar_desconto(1000, "NATAL", hoje)["preco_final"] == 850
    assert aplicar_desconto(1000, None, hoje)["preco_final"] == 1000
    assert aplicar_desconto(1000, "", hoje)["preco_final"] == 1000
