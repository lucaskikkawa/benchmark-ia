import pytest

from descontos import aplicar_desconto


DIA_FORA = "2025-06-15"
DIA_DENTRO = "2024-06-15"


def resultado(preco, cupom, hoje=DIA_FORA):
    return aplicar_desconto(preco, cupom, hoje)


# ---------------------------------------------------------------- contrato geral

def test_dict_tem_exatamente_tres_chaves():
    r = resultado(1000, "OFF10")
    assert set(r.keys()) == {"preco_final", "desconto", "cupom_aplicado"}


def test_desconto_e_preco_menos_final():
    r = resultado(1234, "OFF10")
    assert r["desconto"] == 1234 - r["preco_final"]


def test_sem_cupom_none_nao_altera_preco():
    r = resultado(1234, None)
    assert r == {"preco_final": 1234, "desconto": 0, "cupom_aplicado": None}


def test_cupom_vazio_nao_da_desconto():
    r = resultado(1234, "")
    assert r == {"preco_final": 1234, "desconto": 0, "cupom_aplicado": None}


@pytest.mark.parametrize("cupom", [" ", "\t", " OFF10", "OFF10 ", "off10", "Off10", "OFF 10"])
def test_cupom_com_espaco_ou_caixa_diferente_e_desconhecido(cupom):
    with pytest.raises(ValueError):
        resultado(1000, cupom)


@pytest.mark.parametrize("cupom", ["SEMCUPOM", "OFF20", "FIXO1000", "bemvindo", "natal", "X"])
def test_cupom_desconhecido_levanta_value_error(cupom):
    with pytest.raises(ValueError):
        resultado(1000, cupom)


@pytest.mark.parametrize("cupom", [5, 1.0, b"OFF10", ["OFF10"], {"c": "OFF10"}, object()])
def test_cupom_de_tipo_errado_levanta_type_error(cupom):
    with pytest.raises(TypeError):
        resultado(1000, cupom)


# ---------------------------------------------------------------- preco_centavos

@pytest.mark.parametrize("preco", [True, False])
def test_preco_bool_levanta_type_error(preco):
    with pytest.raises(TypeError):
        resultado(preco, "OFF10")


@pytest.mark.parametrize("preco", [1.0, 100.5, "100", None, [100]])
def test_preco_nao_int_levanta_type_error(preco):
    with pytest.raises(TypeError):
        resultado(preco, None)


def test_preco_negativo_levanta_value_error():
    with pytest.raises(ValueError):
        resultado(-1, None)


def test_preco_negativo_com_cupom_levanta_value_error():
    with pytest.raises(ValueError):
        resultado(-1, "OFF10")


def test_preco_zero_sem_cupom():
    assert resultado(0, None) == {"preco_final": 0, "desconto": 0, "cupom_aplicado": None}


# ---------------------------------------------------------------- hoje

@pytest.mark.parametrize("hoje", [None, 20240101, 2024])
def test_hoje_de_tipo_errado_levanta_type_error(hoje):
    with pytest.raises(TypeError):
        aplicar_desconto(1000, None, hoje)


@pytest.mark.parametrize(
    "hoje",
    [
        "2024-1-01",
        "2024/01/01",
        "01-01-2024",
        "20240101",
        "2024-01-01 ",
        " 2024-01-01",
        "2024-01-01T00:00",
        "2024-13-01",
        "2024-00-10",
        "2024-01-00",
        "2024-02-30",
        "2024-04-31",
        "2023-02-29",
        "1900-02-29",
        "2100-02-29",
        "0000-01-01",
        "10000-01-01",
        "abcd-ef-gh",
        "",
    ],
)
def test_data_invalida_levanta_value_error(hoje):
    with pytest.raises(ValueError):
        aplicar_desconto(1000, None, hoje)


@pytest.mark.parametrize("hoje", ["2000-02-29", "2024-02-29", "0001-12-25", "9999-12-31", "0001-01-01"])
def test_datas_reais_sao_aceitas(hoje):
    r = aplicar_desconto(1000, None, hoje)
    assert r == {"preco_final": 1000, "desconto": 0, "cupom_aplicado": None}


# ---------------------------------------------------------------- OFF10

def test_off10_exemplo_basico():
    assert resultado(1000, "OFF10") == {"preco_final": 900, "desconto": 100, "cupom_aplicado": "OFF10"}


def test_off10_usa_multiplicacao_com_piso_e_nao_subtracao_do_decimo():
    # preco - preco//10 daria 14; a regra correta é (15*90)//100 = 13
    assert resultado(15, "OFF10")["preco_final"] == 13


def test_off10_arredonda_para_baixo_no_preco_final():
    # 199*90 = 17910 -> 179
    r = resultado(199, "OFF10")
    assert r["preco_final"] == 179
    assert r["desconto"] == 20


def test_off10_preco_1_zera_mas_cupom_aplicado():
    assert resultado(1, "OFF10") == {"preco_final": 0, "desconto": 1, "cupom_aplicado": "OFF10"}


def test_off10_preco_0_cupom_conta_como_aplicado():
    assert resultado(0, "OFF10") == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "OFF10"}


@pytest.mark.parametrize("preco", [1, 9, 10, 11, 15, 99, 100, 101, 999, 1000, 123457, 10**12])
def test_off10_formula_exata(preco):
    assert resultado(preco, "OFF10")["preco_final"] == (preco * 90) // 100


# ---------------------------------------------------------------- OFF5

def test_off5_exemplo_200_vira_190():
    assert resultado(200, "OFF5") == {"preco_final": 190, "desconto": 10, "cupom_aplicado": "OFF5"}


def test_off5_101_vira_95():
    assert resultado(101, "OFF5")["preco_final"] == 95


def test_off5_preco_1_zera_mas_cupom_aplicado():
    assert resultado(1, "OFF5") == {"preco_final": 0, "desconto": 1, "cupom_aplicado": "OFF5"}


@pytest.mark.parametrize("preco", [1, 19, 20, 21, 100, 101, 199, 200, 201, 99999])
def test_off5_formula_exata(preco):
    assert resultado(preco, "OFF5")["preco_final"] == (preco * 95) // 100


# ---------------------------------------------------------------- FIXO500

def test_fixo500_desconta_500():
    assert resultado(1000, "FIXO500") == {"preco_final": 500, "desconto": 500, "cupom_aplicado": "FIXO500"}


def test_fixo500_piso_zero_no_limite_exato():
    assert resultado(500, "FIXO500") == {"preco_final": 0, "desconto": 500, "cupom_aplicado": "FIXO500"}


def test_fixo500_piso_zero_quando_preco_menor():
    assert resultado(100, "FIXO500") == {"preco_final": 0, "desconto": 100, "cupom_aplicado": "FIXO500"}


def test_fixo500_um_acima_do_limite():
    assert resultado(501, "FIXO500")["preco_final"] == 1


def test_fixo500_preco_0_cupom_aplicado_sem_desconto():
    assert resultado(0, "FIXO500") == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "FIXO500"}


def test_fixo500_nunca_negativo():
    for preco in range(0, 1200):
        r = resultado(preco, "FIXO500")
        assert r["preco_final"] >= 0
        assert r["desconto"] == preco - r["preco_final"]
        assert r["desconto"] >= 0


# ---------------------------------------------------------------- BEMVINDO

@pytest.mark.parametrize("hoje", ["2024-01-01", "2024-06-15", "2024-12-31"])
def test_bemvindo_dentro_da_janela_inclusive_extremos(hoje):
    assert resultado(1000, "BEMVINDO", hoje) == {
        "preco_final": 800,
        "desconto": 200,
        "cupom_aplicado": "BEMVINDO",
    }


@pytest.mark.parametrize("hoje", ["2023-12-31", "2025-01-01", "2023-01-01", "2025-12-31", "2000-01-01"])
def test_bemvindo_fora_da_janela_nao_altera_preco(hoje):
    assert resultado(1000, "BEMVINDO", hoje) == {
        "preco_final": 1000,
        "desconto": 0,
        "cupom_aplicado": None,
    }


def test_bemvindo_formula_nao_e_subtracao_do_vinte_por_cento():
    # correto: (13*80)//100 = 10; subtração errada: 13 - (13*20)//100 = 11
    assert resultado(13, "BEMVINDO", DIA_DENTRO)["preco_final"] == 10


def test_bemvindo_preco_1_zera_mas_aplicado():
    assert resultado(1, "BEMVINDO", DIA_DENTRO) == {"preco_final": 0, "desconto": 1, "cupom_aplicado": "BEMVINDO"}


@pytest.mark.parametrize("preco", [1, 4, 5, 6, 99, 101, 999, 10**9 + 7])
def test_bemvindo_formula_exata_dentro_da_janela(preco):
    assert resultado(preco, "BEMVINDO", DIA_DENTRO)["preco_final"] == (preco * 80) // 100


def test_bemvindo_fora_da_janela_com_data_dia_vizinho_do_fim_de_2023():
    # 2023-12-31 é o dia imediatamente anterior ao início: não pode aplicar
    assert resultado(1000, "BEMVINDO", "2023-12-31")["cupom_aplicado"] is None


def test_bemvindo_dia_seguinte_ao_fim_de_2024():
    assert resultado(1000, "BEMVINDO", "2025-01-01")["cupom_aplicado"] is None


# ---------------------------------------------------------------- NATAL

@pytest.mark.parametrize("ano", [1, 2000, 2024, 2025, 9999])
def test_natal_24_e_25_de_dezembro_em_qualquer_ano(ano):
    for dia in ("24", "25"):
        hoje = f"{ano:04d}-12-{dia}"
        assert resultado(1000, "NATAL", hoje) == {
            "preco_final": 850,
            "desconto": 150,
            "cupom_aplicado": "NATAL",
        }


@pytest.mark.parametrize("hoje", ["2024-12-23", "2024-12-26", "2024-12-31", "2024-11-25", "2024-01-25", "2024-01-24", "0001-12-26", "9999-12-23"])
def test_natal_fora_dos_dias_nao_altera_preco(hoje):
    assert resultado(1000, "NATAL", hoje) == {
        "preco_final": 1000,
        "desconto": 0,
        "cupom_aplicado": None,
    }


def test_natal_formula_nao_e_subtracao_do_quinze_por_cento():
    # correto: (101*85)//100 = 85; subtração errada: 101 - (101*15)//100 = 86
    assert resultado(101, "NATAL", "2024-12-25")["preco_final"] == 85


def test_natal_preco_1_em_25_12_zera():
    assert resultado(1, "NATAL", "2024-12-25") == {"preco_final": 0, "desconto": 1, "cupom_aplicado": "NATAL"}


def test_natal_preco_0_em_25_12_cupom_aplicado():
    assert resultado(0, "NATAL", "2024-12-25") == {"preco_final": 0, "desconto": 0, "cupom_aplicado": "NATAL"}


@pytest.mark.parametrize("preco", [1, 2, 3, 19, 20, 99, 101, 100000])
def test_natal_formula_exata(preco):
    assert resultado(preco, "NATAL", "2024-12-24")["preco_final"] == (preco * 85) // 100


# ---------------------------------------------------------------- validação de ordem / combinações

def test_cupom_desconhecido_com_data_invalida_levanta_erro():
    # qualquer um dos dois erros é aceitável; o importante é não retornar sucesso
    with pytest.raises((ValueError, TypeError)):
        aplicar_desconto(1000, "XYZ", "2024-02-30")


def test_preco_invalido_com_data_valida_levanta_erro():
    with pytest.raises((ValueError, TypeError)):
        aplicar_desconto(-5, "OFF10", "2024-01-01")


def test_nenhum_cupom_depende_de_hoje_exceto_bemvindo_e_natal():
    for cupom in ("OFF10", "OFF5", "FIXO500"):
        a = aplicar_desconto(1000, cupom, "2000-01-01")
        b = aplicar_desconto(1000, cupom, "2024-12-25")
        assert a == b
