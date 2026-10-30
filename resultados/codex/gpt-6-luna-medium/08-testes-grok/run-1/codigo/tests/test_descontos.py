import pytest

from descontos import aplicar_desconto


def resultado(preco, final, aplicado):
    return {
        "preco_final": final,
        "desconto": preco - final,
        "cupom_aplicado": aplicado,
    }


@pytest.mark.parametrize(
    ("preco", "cupom", "hoje", "final", "aplicado"),
    [
        # Percentuais usam o piso sobre o preço multiplicado, inclusive
        # quando o desconto resultante é menor que um centavo.
        (101, "OFF10", "2024-06-15", 90, "OFF10"),
        (1, "OFF10", "2024-06-15", 0, "OFF10"),
        (200, "OFF5", "2024-06-15", 190, "OFF5"),
        (101, "OFF5", "2024-06-15", 95, "OFF5"),
        (1, "OFF5", "2024-06-15", 0, "OFF5"),
        (101, "BEMVINDO", "2024-06-15", 80, "BEMVINDO"),
        (1, "BEMVINDO", "2024-06-15", 0, "BEMVINDO"),
        (101, "NATAL", "2024-12-24", 85, "NATAL"),
        (1, "NATAL", "2024-12-25", 0, "NATAL"),
        # FIXO500 tem piso zero, mas continua aplicado mesmo com preço zero.
        (100, "FIXO500", "2024-06-15", 0, "FIXO500"),
        (500, "FIXO500", "2024-06-15", 0, "FIXO500"),
        (700, "FIXO500", "2024-06-15", 200, "FIXO500"),
        (0, "FIXO500", "2024-06-15", 0, "FIXO500"),
        # Datas limites inclusivas para BEMVINDO.
        (1000, "BEMVINDO", "2024-01-01", 800, "BEMVINDO"),
        (1000, "BEMVINDO", "2024-12-31", 800, "BEMVINDO"),
        (1000, "BEMVINDO", "2023-12-31", 1000, None),
        (1000, "BEMVINDO", "2025-01-01", 1000, None),
        # NATAL vale em ambos os dias, em qualquer ano, e fora deles não aplica.
        (100, "NATAL", "0001-12-24", 85, "NATAL"),
        (100, "NATAL", "9999-12-25", 85, "NATAL"),
        (1000, "NATAL", "2024-12-23", 1000, None),
        (1000, "NATAL", "2024-12-26", 1000, None),
        (123, None, "2024-06-15", 123, None),
        (123, "", "2024-06-15", 123, None),
    ],
)
def test_regras_de_desconto(preco, cupom, hoje, final, aplicado):
    assert aplicar_desconto(preco, cupom, hoje) == resultado(preco, final, aplicado)


@pytest.mark.parametrize("preco", [True, False, 1.0, 1.5])
def test_preco_deve_ser_int_sem_bool(preco):
    with pytest.raises(TypeError):
        aplicar_desconto(preco, None, "2024-01-01")


def test_preco_negativo_e_invalido():
    with pytest.raises(ValueError):
        aplicar_desconto(-1, None, "2024-01-01")


@pytest.mark.parametrize("cupom", [0, 1, False, [], {}])
def test_cupom_deve_ser_str_ou_none(cupom):
    with pytest.raises(TypeError):
        aplicar_desconto(100, cupom, "2024-01-01")


@pytest.mark.parametrize("cupom", ["OFF10 ", " OFF10", "off10", " ", "\t", "DESCONHECIDO"])
def test_cupom_desconhecido_nao_e_normalizado(cupom):
    with pytest.raises(ValueError):
        aplicar_desconto(100, cupom, "2024-01-01")


@pytest.mark.parametrize("hoje", [None, 20240101, True, b"2024-01-01"])
def test_hoje_deve_ser_str(hoje):
    with pytest.raises(TypeError):
        aplicar_desconto(100, None, hoje)


@pytest.mark.parametrize(
    "hoje",
    [
        "2024-1-01", "2024-01-1", "24-01-01", "2024/01/01", "20240101",
        "2024-01-01 ", " 2024-01-01", "2024-00-10", "2024-13-01",
        "2024-04-31", "1900-02-29", "2100-02-29", "0000-01-01",
    ],
)
def test_data_invalida(hoje):
    with pytest.raises(ValueError):
        aplicar_desconto(100, None, hoje)


@pytest.mark.parametrize("hoje", ["2000-02-29", "0001-12-25", "9999-12-31"])
def test_datas_reais_incluindo_bissexto_e_extremos(hoje):
    assert aplicar_desconto(17, None, hoje) == resultado(17, 17, None)
