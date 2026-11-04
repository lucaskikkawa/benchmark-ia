import pytest

from descontos import aplicar_desconto


# --- contrato do retorno -------------------------------------------------

def test_retorno_tem_exatamente_as_tres_chaves():
    r = aplicar_desconto(1000, None, "2024-06-15")
    assert set(r.keys()) == {"preco_final", "desconto", "cupom_aplicado"}


def test_tipos_do_retorno():
    r = aplicar_desconto(1000, "OFF10", "2024-06-15")
    assert type(r["preco_final"]) is int
    assert type(r["desconto"]) is int
    assert r["cupom_aplicado"] == "OFF10"


# --- sem cupom ------------------------------------------------------------

@pytest.mark.parametrize("cupom", [None, ""])
def test_sem_cupom_nao_altera_preco(cupom):
    r = aplicar_desconto(1234, cupom, "2024-06-15")
    assert r == {"preco_final": 1234, "desconto": 0, "cupom_aplicado": None}


def test_preco_zero_sem_cupom():
    assert aplicar_desconto(0, None, "2024-06-15") == {
        "preco_final": 0,
        "desconto": 0,
        "cupom_aplicado": None,
    }


# --- OFF10 ---------------------------------------------------------------

def test_off10_percentual_simples():
    r = aplicar_desconto(200, "OFF10", "2024-06-15")
    assert r == {"preco_final": 180, "desconto": 20, "cupom_aplicado": "OFF10"}


def test_off10_usa_multiplicacao_e_nao_subtracao_do_piso():
    # preco - preco//10 daria 91; a regra correta é (101*90)//100 = 90
    r = aplicar_desconto(101, "OFF10", "2024-06-15")
    assert r["preco_final"] == 90
    assert r["desconto"] == 11


def test_off10_piso_zera_preco_1_mas_cupom_conta_como_aplicado():
    r = aplicar_desconto(1, "OFF10", "2024-06-15")
    assert r == {"preco_final": 0, "desconto": 1, "cupom_aplicado": "OFF10"}


def test_off10_preco_zero_cupom_aplicado():
    r = aplicar_desconto(0, "OFF10", "2024-06-15")
    assert r == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "OFF10"}


# --- OFF5 ----------------------------------------------------------------

def test_off5_percentual_simples():
    r = aplicar_desconto(200, "OFF5", "2024-06-15")
    assert r == {"preco_final": 190, "desconto": 10, "cupom_aplicado": "OFF5"}


def test_off5_arredondamento_do_piso():
    # (101*95)//100 = 95
    r = aplicar_desconto(101, "OFF5", "2024-06-15")
    assert r["preco_final"] == 95
    assert r["desconto"] == 6


def test_off5_preco_1_piso_zera_e_cupom_aplicado():
    # (1*95)//100 = 0
    r = aplicar_desconto(1, "OFF5", "2024-06-15")
    assert r == {"preco_final": 0, "desconto": 1, "cupom_aplicado": "OFF5"}


# --- FIXO500 -------------------------------------------------------------

def test_fixo500_desconto_normal():
    r = aplicar_desconto(1000, "FIXO500", "2024-06-15")
    assert r == {"preco_final": 500, "desconto": 500, "cupom_aplicado": "FIXO500"}


def test_fixo500_exatamente_no_valor():
    r = aplicar_desconto(500, "FIXO500", "2024-06-15")
    assert r == {"preco_final": 0, "desconto": 500, "cupom_aplicado": "FIXO500"}


def test_fixo500_piso_zero_nunca_negativo():
    r = aplicar_desconto(100, "FIXO500", "2024-06-15")
    assert r == {"preco_final": 0, "desconto": 100, "cupom_aplicado": "FIXO500"}


def test_fixo500_preco_zero_cupom_aplicado():
    r = aplicar_desconto(0, "FIXO500", "2024-06-15")
    assert r == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "FIXO500"}


def test_fixo500_um_centavo_acima_do_valor():
    r = aplicar_desconto(501, "FIXO500", "2024-06-15")
    assert r["preco_final"] == 1
    assert r["desconto"] == 500


# --- BEMVINDO (2024-01-01 .. 2024-12-31, inclusive) -------------------------

@pytest.mark.parametrize("hoje", ["2024-01-01", "2024-06-15", "2024-12-31"])
def test_bemvindo_dentro_da_janela_inclusive_extremos(hoje):
    r = aplicar_desconto(200, "BEMVINDO", hoje)
    assert r == {"preco_final": 160, "desconto": 40, "cupom_aplicado": "BEMVINDO"}


def test_bemvindo_usa_multiplicacao_e_nao_subtracao_do_piso():
    # preco - (preco*20)//100 daria 81; a regra correta é (101*80)//100 = 80
    r = aplicar_desconto(101, "BEMVINDO", "2024-06-15")
    assert r["preco_final"] == 80
    assert r["desconto"] == 21


@pytest.mark.parametrize("hoje", ["2023-12-31", "2025-01-01", "2030-07-04", "2023-06-01"])
def test_bemvindo_fora_da_janela_nao_altera(hoje):
    r = aplicar_desconto(200, "BEMVINDO", hoje)
    assert r == {"preco_final": 200, "desconto": 0, "cupom_aplicado": None}


@pytest.mark.parametrize("hoje", ["2024-01-02", "2024-12-30"])
def test_bemvindo_perto_das_bordas_dentro_da_janela_aplica(hoje):
    assert aplicar_desconto(200, "BEMVINDO", hoje)["cupom_aplicado"] == "BEMVINDO"


def test_bemvindo_piso_preco_1():
    r = aplicar_desconto(1, "BEMVINDO", "2024-01-01")
    assert r == {"preco_final": 0, "desconto": 1, "cupom_aplicado": "BEMVINDO"}


# --- NATAL (24 e 25 de dezembro, qualquer ano) ------------------------------

@pytest.mark.parametrize(
    "hoje",
    ["2024-12-24", "2024-12-25", "1990-12-24", "1990-12-25", "0001-12-25", "9999-12-24", "9999-12-25"],
)
def test_natal_nos_dias_certos_em_qualquer_ano(hoje):
    r = aplicar_desconto(200, "NATAL", hoje)
    assert r == {"preco_final": 170, "desconto": 30, "cupom_aplicado": "NATAL"}


def test_natal_usa_multiplicacao_e_nao_subtracao_do_piso():
    # preco - (preco*15)//100 daria 86; a regra correta é (101*85)//100 = 85
    r = aplicar_desconto(101, "NATAL", "2024-12-25")
    assert r["preco_final"] == 85
    assert r["desconto"] == 16


def test_natal_piso_preco_1_em_25_12():
    r = aplicar_desconto(1, "NATAL", "2024-12-25")
    assert r == {"preco_final": 0, "desconto": 1, "cupom_aplicado": "NATAL"}


@pytest.mark.parametrize(
    "hoje",
    ["2024-12-23", "2024-12-26", "2024-11-25", "2024-01-25", "2024-12-31", "2024-01-24"],
)
def test_natal_fora_dos_dias_nao_altera(hoje):
    r = aplicar_desconto(200, "NATAL", hoje)
    assert r == {"preco_final": 200, "desconto": 0, "cupom_aplicado": None}


def test_natal_nao_depende_so_do_dia_do_mes():
    # dia 24 de outro mês não é natal
    assert aplicar_desconto(200, "NATAL", "2024-11-24")["cupom_aplicado"] is None
    assert aplicar_desconto(200, "NATAL", "2024-11-25")["cupom_aplicado"] is None


# --- cupom: tipo, vazio e desconhecido -------------------------------------

@pytest.mark.parametrize("cupom", [1, 0, b"OFF10", ["OFF10"], {"OFF10": 1}, 1.5])
def test_cupom_de_tipo_errado_levanta_typeerror(cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(100, cupom, "2024-06-15")


@pytest.mark.parametrize("cupom", [" ", "\t", " OFF10", "OFF10 ", "\nOFF10", "off10", "Off10", "OFF 10"])
def test_cupom_com_espaco_ou_caixa_diferente_levanta_valueerror(cupom):
    # não há strip nem normalização de caixa
    with pytest.raises(ValueError):
        aplicar_desconto(100, cupom, "2024-06-15")


@pytest.mark.parametrize("cupom", ["XYZ", "OFF20", "FIXO5", "bemvindo", "NATAL2", "OFF10OFF5"])
def test_cupom_desconhecido_levanta_valueerror(cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(100, cupom, "2024-06-15")


# --- preco_centavos ------------------------------------------------------

@pytest.mark.parametrize("preco", [True, False, 1.0, 100.0, "100", None, [100]])
def test_preco_de_tipo_errado_levanta_typeerror(preco):
    with pytest.raises(TypeError):
        aplicar_desconto(preco, None, "2024-06-15")


def test_preco_bool_nao_vale_mesmo_com_cupom():
    with pytest.raises(TypeError):
        aplicar_desconto(True, "OFF10", "2024-06-15")


@pytest.mark.parametrize("preco", [-1, -100])
def test_preco_negativo_levanta_valueerror(preco):
    with pytest.raises(ValueError):
        aplicar_desconto(preco, "OFF10", "2024-06-15")


# --- hoje: formato e calendário -----------------------------------------

@pytest.mark.parametrize("hoje", [2024, None, 20240615, b"2024-06-15", ["2024-06-15"]])
def test_hoje_de_tipo_errado_levanta_typeerror(hoje):
    with pytest.raises(TypeError):
        aplicar_desconto(100, None, hoje)


@pytest.mark.parametrize(
    "hoje",
    [
        "",
        "2024-6-15",
        "2024-06-5",
        "24-06-15",
        "2024/06/15",
        "2024-06-15 ",
        " 2024-06-15",
        "2024-06-15T00:00",
        "20240615",
        "2024-13-01",
        "2024-00-10",
        "2024-12-32",
        "2024-06-00",
        "0000-12-25",
        "abcd-ef-gh",
    ],
)
def test_formato_de_data_invalido_levanta_valueerror(hoje):
    with pytest.raises(ValueError):
        aplicar_desconto(100, None, hoje)


@pytest.mark.parametrize("hoje", ["2023-02-29", "2100-02-29", "1900-02-29", "2019-02-29", "2024-04-31"])
def test_data_inexistente_levanta_valueerror(hoje):
    with pytest.raises(ValueError):
        aplicar_desconto(100, "NATAL", hoje)


@pytest.mark.parametrize("hoje", ["2000-02-29", "2024-02-29", "2400-02-29", "9999-12-31"])
def test_data_real_valida_nao_levanta(hoje):
    r = aplicar_desconto(100, None, hoje)
    assert r["cupom_aplicado"] is None


def test_29_fev_2000_existe_e_nao_e_natal():
    r = aplicar_desconto(100, "NATAL", "2000-02-29")
    assert r["cupom_aplicado"] is None


def test_data_invalida_com_cupom_valido_levanta_valueerror():
    # a data é validada mesmo quando o cupom não usaria a data
    with pytest.raises(ValueError):
        aplicar_desconto(100, "OFF10", "1900-02-29")


def test_data_invalida_com_cupom_none_levanta_valueerror():
    with pytest.raises(ValueError):
        aplicar_desconto(100, None, "2023-02-29")
