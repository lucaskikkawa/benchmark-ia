import pytest

from descuentos import aplicar_desconto


def resultado(preco_final, desconto, cupom_aplicado):
    return {
        "preco_final": preco_final,
        "desconto": desconto,
        "cupom_aplicado": cupom_aplicado,
    }


@pytest.mark.parametrize(
    ("preco", "cupom", "hoje", "esperado"),
    [
        (0, None, "2024-06-15", resultado(0, 0, None)),
        (123, "", "2024-06-15", resultado(123, 0, None)),
        # Os percentuais são calculados sobre o preço e arredondados para baixo.
        (101, "OFF10", "2024-06-15", resultado(90, 11, "OFF10")),
        (1, "OFF10", "2024-06-15", resultado(0, 1, "OFF10")),
        (200, "OFF5", "2024-06-15", resultado(190, 10, "OFF5")),
        (101, "OFF5", "2024-06-15", resultado(95, 6, "OFF5")),
        (1, "OFF5", "2024-06-15", resultado(0, 1, "OFF5")),
        # O piso é aplicado ao preço final; o desconto continua sendo a diferença.
        (100, "FIXO500", "2024-06-15", resultado(0, 100, "FIXO500")),
        (0, "FIXO500", "2024-06-15", resultado(0, 0, "FIXO500")),
        (700, "FIXO500", "2024-06-15", resultado(200, 500, "FIXO500")),
        # BEMVINDO inclui os dois extremos da janela de 2024.
        (101, "BEMVINDO", "2024-01-01", resultado(80, 21, "BEMVINDO")),
        (101, "BEMVINDO", "2024-12-31", resultado(80, 21, "BEMVINDO")),
        (1, "BEMVINDO", "2024-06-15", resultado(0, 1, "BEMVINDO")),
        (100, "BEMVINDO", "2023-12-31", resultado(100, 0, None)),
        (100, "BEMVINDO", "2025-01-01", resultado(100, 0, None)),
        # NATAL vale em 24 e 25/12 em qualquer ano, inclusive ano 0001.
        (101, "NATAL", "2024-12-24", resultado(85, 16, "NATAL")),
        (101, "NATAL", "2024-12-25", resultado(85, 16, "NATAL")),
        (1, "NATAL", "2025-12-25", resultado(0, 1, "NATAL")),
        (100, "NATAL", "0001-12-24", resultado(85, 15, "NATAL")),
        (100, "NATAL", "9999-12-25", resultado(85, 15, "NATAL")),
        (100, "NATAL", "2024-12-23", resultado(100, 0, None)),
        (100, "NATAL", "2024-12-26", resultado(100, 0, None)),
        (100, "NATAL", "2024-11-25", resultado(100, 0, None)),
    ],
)
def test_aplica_regras_e_devolve_dict_exato(preco, cupom, hoje, esperado):
    obtido = aplicar_desconto(preco, cupom, hoje)

    assert obtido == esperado
    assert set(obtido) == {"preco_final", "desconto", "cupom_aplicado"}
    assert type(obtido["preco_final"]) is int
    assert type(obtido["desconto"]) is int


@pytest.mark.parametrize("preco", [0, 1, 2, 9, 10, 11, 19, 99, 101, 109, 999])
@pytest.mark.parametrize("cupom, fator", [("OFF10", 90), ("OFF5", 95)])
def test_percentuais_usam_piso_no_preco_final(preco, cupom, fator):
    final = (preco * fator) // 100
    assert aplicar_desconto(preco, cupom, "2024-06-15") == resultado(
        final, preco - final, cupom
    )


@pytest.mark.parametrize("preco", [0, 1, 2, 99, 100, 499, 500, 501, 999])
def test_fixo500_tem_piso_zero(preco):
    final = max(0, preco - 500)
    assert aplicar_desconto(preco, "FIXO500", "2024-06-15") == resultado(
        final, preco - final, "FIXO500"
    )


@pytest.mark.parametrize("preco", [0, 1, 2, 9, 99, 101, 999])
def test_bemvindo_usa_piso_no_preco_final(preco):
    final = (preco * 80) // 100
    assert aplicar_desconto(preco, "BEMVINDO", "2024-06-15") == resultado(
        final, preco - final, "BEMVINDO"
    )


@pytest.mark.parametrize("preco", [0, 1, 2, 9, 99, 101, 999])
def test_natal_usa_piso_no_preco_final(preco):
    final = (preco * 85) // 100
    assert aplicar_desconto(preco, "NATAL", "2024-12-24") == resultado(
        final, preco - final, "NATAL"
    )


@pytest.mark.parametrize("preco", [0, 1, 100, 12345])
@pytest.mark.parametrize("cupom", [None, ""])
def test_cupom_ausente_ou_vazio_nao_altera_preco(preco, cupom):
    assert aplicar_desconto(preco, cupom, "2024-06-15") == resultado(preco, 0, None)


@pytest.mark.parametrize("cupom", [" ", "\t", "OFF10 ", " OFF10", "off10", "off5", "NATAL\n"])
def test_texto_desconhecido_nao_e_normalizado(cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(100, cupom, "2024-06-15")


@pytest.mark.parametrize("cupom", ["OUTRO", "FIXO", "BEM VINDO", "NATAL!", "10%"])
def test_cupom_desconhecido_levanta_value_error(cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(100, cupom, "2024-06-15")


@pytest.mark.parametrize("preco", [-1, -100])
def test_preco_negativo_levanta_value_error(preco):
    with pytest.raises(ValueError):
        aplicar_desconto(preco, "OFF10", "2024-06-15")


@pytest.mark.parametrize("preco", [True, False, 1.0, 1.5, "100", None])
def test_preco_deve_ser_int_sem_aceitar_bool(preco):
    with pytest.raises(TypeError):
        aplicar_desconto(preco, "OFF10", "2024-06-15")


@pytest.mark.parametrize("cupom", [1, 10.0, True, [], {}])
def test_cupom_deve_ser_str_ou_none(cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(100, cupom, "2024-06-15")


@pytest.mark.parametrize("hoje", [None, 20240101, True, b"2024-01-01"])
def test_data_deve_ser_str(hoje):
    with pytest.raises(TypeError):
        aplicar_desconto(100, "OFF10", hoje)


@pytest.mark.parametrize(
    "hoje",
    [
        "",
        "2024-1-01",
        "2024-01-1",
        "24-01-01",
        "2024/01/01",
        "2024-01-01 ",
        " 2024-01-01",
        "0000-01-01",
        "10000-01-01",
        "2024-00-01",
        "2024-13-01",
        "2024-01-00",
        "2024-01-32",
        "2023-02-29",
        "1900-02-29",
        "2100-02-29",
        "2024-04-31",
        "2024-02-30",
    ],
)
def test_data_formato_ou_dia_invalido_levanta_value_error(hoje):
    with pytest.raises(ValueError):
        aplicar_desconto(100, "OFF10", hoje)


@pytest.mark.parametrize("hoje", ["2000-02-29", "2024-02-29", "0001-12-25", "9999-12-31"])
def test_datas_reais_nos_extremos_do_calendario_sao_aceitas(hoje):
    assert aplicar_desconto(100, None, hoje) == resultado(100, 0, None)


def test_preco_inteiro_grande_mantem_calculo_exato():
    preco = 10**30 + 1
    final = (preco * 90) // 100
    assert aplicar_desconto(preco, "OFF10", "2024-06-15") == resultado(
        final, preco - final, "OFF10"
    )

