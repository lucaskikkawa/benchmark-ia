"""Testes do contrato de descontos.aplicar_desconto."""

from datetime import date, timedelta

import pytest

from descontos import aplicar_desconto

DIA_COMUM = "2023-06-15"
CHAVES = {"preco_final", "desconto", "cupom_aplicado"}


def _checa(res, preco, final, cupom):
    assert type(res) is dict
    assert set(res) == CHAVES
    assert type(res["preco_final"]) is int
    assert type(res["desconto"]) is int
    assert res["preco_final"] == final
    assert res["desconto"] == preco - final
    assert res["cupom_aplicado"] == cupom
    if cupom is None:
        assert res["cupom_aplicado"] is None
    else:
        assert type(res["cupom_aplicado"]) is str


def _dias(inicio, fim):
    for n in range((fim - inicio).days + 1):
        yield inicio + timedelta(days=n)


PRECOS = list(range(0, 1201)) + [1999, 9999, 10**6 + 7, 10**15 + 3, 10**30 + 99]


# ---------------------------------------------------------------- formato

def test_formato_do_retorno():
    res = aplicar_desconto(1000, None, DIA_COMUM)
    _checa(res, 1000, 1000, None)
    assert len(res) == 3


@pytest.mark.parametrize("cupom", ["OFF10", "OFF5", "FIXO500"])
def test_formato_com_cupom(cupom):
    res = aplicar_desconto(1234, cupom, DIA_COMUM)
    assert set(res) == CHAVES
    assert len(res) == 3
    assert res["cupom_aplicado"] == cupom


# ---------------------------------------------------------------- cupom vazio

@pytest.mark.parametrize("cupom", [None, ""])
@pytest.mark.parametrize("preco", [0, 1, 99, 100, 501, 123456, 10**20])
def test_sem_cupom_nao_muda(cupom, preco):
    _checa(aplicar_desconto(preco, cupom, DIA_COMUM), preco, preco, None)


@pytest.mark.parametrize("cupom", [None, ""])
@pytest.mark.parametrize("hoje", ["2024-01-01", "2024-12-25", "2024-12-24", "0001-01-01", "9999-12-31"])
def test_sem_cupom_em_datas_especiais(cupom, hoje):
    _checa(aplicar_desconto(500, cupom, hoje), 500, 500, None)


# ---------------------------------------------------------------- OFF10

@pytest.mark.parametrize(
    "preco,final",
    [(0, 0), (1, 0), (5, 4), (9, 8), (10, 9), (11, 9), (19, 17), (99, 89),
     (100, 90), (101, 90), (109, 98), (1000, 900), (1999, 1799)],
)
def test_off10_exemplos(preco, final):
    _checa(aplicar_desconto(preco, "OFF10", DIA_COMUM), preco, final, "OFF10")


def test_off10_preco_1_aplica_mesmo_com_desconto_zerado_pelo_piso():
    res = aplicar_desconto(1, "OFF10", DIA_COMUM)
    assert res == {"preco_final": 0, "desconto": 1, "cupom_aplicado": "OFF10"}


def test_off10_preco_zero_conta_como_aplicado():
    res = aplicar_desconto(0, "OFF10", DIA_COMUM)
    assert res == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "OFF10"}


@pytest.mark.parametrize("preco", PRECOS)
def test_off10_formula(preco):
    _checa(aplicar_desconto(preco, "OFF10", DIA_COMUM), preco, (preco * 90) // 100, "OFF10")


# ---------------------------------------------------------------- OFF5

@pytest.mark.parametrize(
    "preco,final",
    [(0, 0), (1, 0), (19, 18), (20, 19), (21, 19), (100, 95), (101, 95),
     (119, 113), (200, 190), (1999, 1899)],
)
def test_off5_exemplos(preco, final):
    _checa(aplicar_desconto(preco, "OFF5", DIA_COMUM), preco, final, "OFF5")


def test_off5_exemplos_do_enunciado():
    assert aplicar_desconto(200, "OFF5", DIA_COMUM) == {
        "preco_final": 190, "desconto": 10, "cupom_aplicado": "OFF5"}
    assert aplicar_desconto(101, "OFF5", DIA_COMUM) == {
        "preco_final": 95, "desconto": 6, "cupom_aplicado": "OFF5"}


@pytest.mark.parametrize("preco", PRECOS)
def test_off5_formula(preco):
    _checa(aplicar_desconto(preco, "OFF5", DIA_COMUM), preco, (preco * 95) // 100, "OFF5")


# ---------------------------------------------------------------- FIXO500

@pytest.mark.parametrize(
    "preco,final",
    [(0, 0), (1, 0), (100, 0), (499, 0), (500, 0), (501, 1), (999, 499),
     (1000, 500), (10**20, 10**20 - 500)],
)
def test_fixo500_exemplos(preco, final):
    _checa(aplicar_desconto(preco, "FIXO500", DIA_COMUM), preco, final, "FIXO500")


def test_fixo500_piso_preco_100():
    assert aplicar_desconto(100, "FIXO500", DIA_COMUM) == {
        "preco_final": 0, "desconto": 100, "cupom_aplicado": "FIXO500"}


def test_fixo500_preco_zero_conta_como_aplicado():
    assert aplicar_desconto(0, "FIXO500", DIA_COMUM) == {
        "preco_final": 0, "desconto": 0, "cupom_aplicado": "FIXO500"}


@pytest.mark.parametrize("preco", PRECOS)
def test_fixo500_formula(preco):
    res = aplicar_desconto(preco, "FIXO500", DIA_COMUM)
    _checa(res, preco, max(0, preco - 500), "FIXO500")
    assert res["preco_final"] >= 0
    assert 0 <= res["desconto"] <= 500


# ---------------------------------------------------------------- BEMVINDO

@pytest.mark.parametrize("hoje", ["2024-01-01", "2024-12-31", "2024-02-29", "2024-06-15", "2024-12-25"])
@pytest.mark.parametrize(
    "preco,final", [(0, 0), (1, 0), (4, 3), (6, 4), (9, 7), (99, 79), (100, 80), (101, 80), (1999, 1599)]
)
def test_bemvindo_dentro_da_janela(hoje, preco, final):
    _checa(aplicar_desconto(preco, "BEMVINDO", hoje), preco, final, "BEMVINDO")


def test_bemvindo_extremos():
    assert aplicar_desconto(1000, "BEMVINDO", "2024-01-01") == {
        "preco_final": 800, "desconto": 200, "cupom_aplicado": "BEMVINDO"}
    assert aplicar_desconto(1000, "BEMVINDO", "2024-12-31") == {
        "preco_final": 800, "desconto": 200, "cupom_aplicado": "BEMVINDO"}


@pytest.mark.parametrize(
    "hoje",
    ["2023-12-31", "2025-01-01", "2023-12-30", "2025-01-02", "2023-01-01",
     "2025-12-31", "0001-01-01", "9999-12-31", "2023-12-25", "2025-12-24"],
)
@pytest.mark.parametrize("preco", [0, 1, 100, 1000, 12345])
def test_bemvindo_fora_da_janela(hoje, preco):
    _checa(aplicar_desconto(preco, "BEMVINDO", hoje), preco, preco, None)


def test_bemvindo_fora_da_janela_exemplos():
    for hoje in ("2023-12-31", "2025-01-01"):
        assert aplicar_desconto(1000, "BEMVINDO", hoje) == {
            "preco_final": 1000, "desconto": 0, "cupom_aplicado": None}


@pytest.mark.parametrize("preco", PRECOS)
def test_bemvindo_formula(preco):
    _checa(aplicar_desconto(preco, "BEMVINDO", "2024-07-01"), preco, (preco * 80) // 100, "BEMVINDO")


def test_bemvindo_todos_os_dias_de_2023_a_2025():
    for d in _dias(date(2023, 1, 1), date(2025, 12, 31)):
        res = aplicar_desconto(1000, "BEMVINDO", d.isoformat())
        if d.year == 2024:
            _checa(res, 1000, 800, "BEMVINDO")
        else:
            _checa(res, 1000, 1000, None)


# ---------------------------------------------------------------- NATAL

@pytest.mark.parametrize(
    "hoje", ["2024-12-24", "2024-12-25", "2023-12-24", "2023-12-25", "0001-12-25",
             "0001-12-24", "9999-12-24", "9999-12-25", "1900-12-25", "2100-12-24"]
)
@pytest.mark.parametrize(
    "preco,final", [(0, 0), (1, 0), (6, 5), (7, 5), (19, 16), (99, 84), (100, 85), (101, 85), (1999, 1699)]
)
def test_natal_nos_dias(hoje, preco, final):
    _checa(aplicar_desconto(preco, "NATAL", hoje), preco, final, "NATAL")


def test_natal_preco_1_em_25_dezembro():
    assert aplicar_desconto(1, "NATAL", "2024-12-25") == {
        "preco_final": 0, "desconto": 1, "cupom_aplicado": "NATAL"}


def test_natal_24_e_25():
    for hoje in ("2023-12-24", "2023-12-25"):
        assert aplicar_desconto(1000, "NATAL", hoje) == {
            "preco_final": 850, "desconto": 150, "cupom_aplicado": "NATAL"}


@pytest.mark.parametrize(
    "hoje", ["2024-12-23", "2024-12-26", "2024-12-31", "2024-01-01", "2024-11-24",
             "2024-11-25", "2024-01-24", "2024-01-25", "2024-06-25", "2025-01-01",
             "0001-01-01", "9999-12-31", "2024-12-12", "2024-10-25"]
)
@pytest.mark.parametrize("preco", [0, 1, 100, 1000])
def test_natal_fora_dos_dias(hoje, preco):
    _checa(aplicar_desconto(preco, "NATAL", hoje), preco, preco, None)


@pytest.mark.parametrize("preco", PRECOS)
def test_natal_formula(preco):
    _checa(aplicar_desconto(preco, "NATAL", "2022-12-25"), preco, (preco * 85) // 100, "NATAL")


@pytest.mark.parametrize("ano", [1, 4, 100, 1900, 2000, 2023, 2024, 2100, 9999])
def test_natal_todos_os_dias_do_ano(ano):
    for d in _dias(date(ano, 1, 1), date(ano, 12, 31)):
        res = aplicar_desconto(1000, "NATAL", d.isoformat())
        if (d.month, d.day) in ((12, 24), (12, 25)):
            _checa(res, 1000, 850, "NATAL")
        else:
            _checa(res, 1000, 1000, None)


# ---------------------------------------------------------------- cupons inválidos

@pytest.mark.parametrize(
    "cupom",
    [" ", "\t", "\n", "  ", " OFF10", "OFF10 ", "off10", "Off10", "OFF 10", "OFF1",
     "OFF100", "OFF", "off5", " OFF5", "OFF5 ", "fixo500", "FIXO50", "FIXO5000",
     "FIXO500 ", "bemvindo", "BemVindo", " BEMVINDO", "BEMVINDO ", "natal", "Natal",
     "NATAL ", " NATAL", "\tNATAL", "DESCONTO", "XYZ", "None", "0", "OFF10OFF5",
     "OFF10\n", "OFF10\x00", "ＯＦＦ１０"],
)
def test_cupom_desconhecido(cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom, DIA_COMUM)


@pytest.mark.parametrize("cupom", [" ", "\t", "desconhecido", "off10"])
@pytest.mark.parametrize("hoje", ["2024-06-01", "2024-12-25", "2023-01-01"])
def test_cupom_desconhecido_em_qualquer_data(cupom, hoje):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom, hoje)


@pytest.mark.parametrize("preco", [0, 1, 10**20])
def test_cupom_desconhecido_qualquer_preco(preco):
    with pytest.raises(ValueError):
        aplicar_desconto(preco, "INVALIDO", DIA_COMUM)


@pytest.mark.parametrize("cupom", [10, 0, 1.5, b"OFF10", ["OFF10"], ("OFF10",), {"OFF10"}, True, False, object()])
def test_cupom_tipo_errado(cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom, DIA_COMUM)


# ---------------------------------------------------------------- preço

@pytest.mark.parametrize("preco", [-1, -2, -100, -500, -10**20])
@pytest.mark.parametrize("cupom", [None, "", "OFF10", "OFF5", "FIXO500"])
def test_preco_negativo(preco, cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(preco, cupom, DIA_COMUM)


@pytest.mark.parametrize("cupom,hoje", [("BEMVINDO", "2024-05-05"), ("BEMVINDO", "2023-05-05"),
                                        ("NATAL", "2024-12-25"), ("NATAL", "2024-12-26")])
def test_preco_negativo_cupons_de_data(cupom, hoje):
    with pytest.raises(ValueError):
        aplicar_desconto(-1, cupom, hoje)


@pytest.mark.parametrize("preco", [True, False, 1.0, 0.0, 100.0, 99.5, "100", None, [100], 1 + 0j])
@pytest.mark.parametrize("cupom", [None, "OFF10", "FIXO500"])
def test_preco_tipo_errado(preco, cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(preco, cupom, DIA_COMUM)


def test_preco_zero_valido():
    _checa(aplicar_desconto(0, None, DIA_COMUM), 0, 0, None)


def test_preco_inteiro_grande_exato():
    preco = 10**30 + 99
    assert aplicar_desconto(preco, "OFF10", DIA_COMUM)["preco_final"] == (preco * 90) // 100
    assert aplicar_desconto(preco, "OFF5", DIA_COMUM)["preco_final"] == (preco * 95) // 100


# ---------------------------------------------------------------- data

DATAS_VALIDAS = [
    "2000-02-29", "0001-12-25", "0001-01-01", "9999-12-31", "2024-02-29", "1600-02-29",
    "2400-02-29", "0004-02-29", "2023-02-28", "1900-02-28", "2100-02-28", "2024-01-31",
    "2024-03-31", "2024-04-30", "2024-12-31",
]


@pytest.mark.parametrize("hoje", DATAS_VALIDAS)
@pytest.mark.parametrize("cupom", [None, "", "OFF10", "FIXO500", "BEMVINDO", "NATAL"])
def test_datas_validas(hoje, cupom):
    res = aplicar_desconto(1000, cupom, hoje)
    assert set(res) == CHAVES


DATAS_INVALIDAS = [
    "1900-02-29", "2100-02-29", "2023-02-29", "2200-02-29", "0100-02-29", "2024-02-30",
    "2024-02-31", "2024-04-31", "2024-06-31", "2024-09-31", "2024-11-31", "2024-01-32",
    "2024-13-01", "2024-00-10", "2024-01-00", "0000-01-01", "0000-12-25", "2024-12-32",
    "", "2024", "2024-1-1", "2024-01-1", "24-01-01", "2024/01/01", "2024.01.01",
    "01-01-2024", "25-12-2024", "2024-12-25 ", " 2024-12-25", "2024-12-25T00:00",
    "2024-12-25T00:00:00", "20241225", "2024-W52-3", "2024-360", "aaaa-bb-cc",
    "2024-ab-01", "hoje", "2024--12-25", "2024-12--5", "+2024-12-25",
]


@pytest.mark.parametrize("hoje", DATAS_INVALIDAS)
@pytest.mark.parametrize("cupom", [None, "", "OFF10", "OFF5", "FIXO500", "BEMVINDO", "NATAL"])
def test_data_invalida(hoje, cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, cupom, hoje)


@pytest.mark.parametrize("hoje", [None, 20241225, 2024.12, date(2024, 12, 25), b"2024-12-25",
                                  ["2024-12-25"], ("2024", "12", "25")])
@pytest.mark.parametrize("cupom", [None, "OFF10", "NATAL", "BEMVINDO"])
def test_data_tipo_errado(hoje, cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, cupom, hoje)


def test_validade_de_todos_os_dias_em_anos_chave():
    for ano in (1, 4, 100, 400, 1900, 2000, 2023, 2024, 2100, 9999):
        for mes in range(1, 13):
            for dia in range(1, 33):
                hoje = f"{ano:04d}-{mes:02d}-{dia:02d}"
                try:
                    date(ano, mes, dia)
                except ValueError:
                    with pytest.raises(ValueError):
                        aplicar_desconto(100, None, hoje)
                else:
                    _checa(aplicar_desconto(100, None, hoje), 100, 100, None)
                    _checa(aplicar_desconto(100, "OFF10", hoje), 100, 90, "OFF10")


def test_29_fevereiro_regra_do_seculo():
    for ano in range(1, 10000):
        hoje = f"{ano:04d}-02-29"
        bissexto = ano % 4 == 0 and (ano % 100 != 0 or ano % 400 == 0)
        if bissexto:
            _checa(aplicar_desconto(100, None, hoje), 100, 100, None)
        else:
            with pytest.raises(ValueError):
                aplicar_desconto(100, None, hoje)


# ---------------------------------------------------------------- não mutação / determinismo

def test_chamadas_repetidas_sao_independentes():
    a = aplicar_desconto(1000, "OFF10", DIA_COMUM)
    a["preco_final"] = -1
    b = aplicar_desconto(1000, "OFF10", DIA_COMUM)
    assert b == {"preco_final": 900, "desconto": 100, "cupom_aplicado": "OFF10"}
    assert a is not b
