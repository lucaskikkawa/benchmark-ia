import pytest

from frete import cotar

FAIXAS = (
    ("carta", 1, 300, 800, 0),
    ("pac", 301, 2000, 1500, 2),
    ("sedex", 2001, 10000, 2500, 5),
    ("transportadora", 10001, 30000, 4000, 8),
)


def _esperado(peso, distancia, expresso):
    for nome, minimo, maximo, base, por_km in FAIXAS:
        if minimo <= peso <= maximo:
            valor = base + por_km * distancia
            if expresso:
                valor = (valor * 3) // 2
            return {"faixa": nome, "valor_centavos": valor, "expresso": expresso}
    raise AssertionError(peso)


def test_exemplos_do_enunciado():
    assert cotar(300, 100, False) == {
        "faixa": "carta",
        "valor_centavos": 800,
        "expresso": False,
    }
    assert cotar(301, 1, True) == {
        "faixa": "pac",
        "valor_centavos": 2253,
        "expresso": True,
    }
    assert cotar(10001, 1, False) == {
        "faixa": "transportadora",
        "valor_centavos": 4008,
        "expresso": False,
    }


def test_fronteiras_de_peso_e_distancia():
    pesos = [1, 300, 301, 2000, 2001, 10000, 10001, 30000]
    distancias = [0, 1, 3000]
    for peso in pesos:
        for distancia in distancias:
            for expresso in (False, True):
                assert cotar(peso, distancia, expresso) == _esperado(
                    peso, distancia, expresso
                )


def test_carta_ignora_distancia():
    assert cotar(1, 0, False)["valor_centavos"] == 800
    assert cotar(300, 3000, False)["valor_centavos"] == 800
    assert cotar(300, 3000, True)["valor_centavos"] == 1200


def test_expresso_divisao_inteira():
    assert cotar(2000, 1, False)["valor_centavos"] == 1502
    assert cotar(2000, 1, True)["valor_centavos"] == (1502 * 3) // 2


def test_peso_invalido():
    for peso in (0, -1, 30001, 10**6):
        with pytest.raises(ValueError):
            cotar(peso, 0, False)


def test_distancia_invalida():
    with pytest.raises(ValueError):
        cotar(100, -1, False)
    with pytest.raises(ValueError):
        cotar(100, 3001, True)


def test_tipos_invalidos():
    with pytest.raises(TypeError):
        cotar(True, 0, False)
    with pytest.raises(TypeError):
        cotar(False, 0, False)
    with pytest.raises(TypeError):
        cotar(10.0, 0, False)
    with pytest.raises(TypeError):
        cotar(10, True, False)
    with pytest.raises(TypeError):
        cotar(10, 1.5, False)
    with pytest.raises(TypeError):
        cotar(10, 0, 1)
    with pytest.raises(TypeError):
        cotar(10, 0, "sim")
    with pytest.raises(TypeError):
        cotar("10", 0, False)


def test_chaves_e_tipo_do_valor():
    resultado = cotar(500, 10, True)
    assert set(resultado) == {"faixa", "valor_centavos", "expresso"}
    assert isinstance(resultado["valor_centavos"], int)
    assert resultado["expresso"] is True


def test_estrutura_tabela_e_faixa():
    from frete import TabelaFrete, faixa_de_peso

    assert isinstance(TabelaFrete, type)
    assert tuple(TabelaFrete.FAIXAS) == FAIXAS
    tabela = TabelaFrete()
    for peso, nome in (
        (1, "carta"),
        (300, "carta"),
        (301, "pac"),
        (2000, "pac"),
        (2001, "sedex"),
        (10000, "sedex"),
        (10001, "transportadora"),
        (30000, "transportadora"),
    ):
        assert faixa_de_peso(peso) == nome
        assert tabela.cotar(peso, 15, False) == cotar(peso, 15, False)
        assert tabela.cotar(peso, 15, True) == cotar(peso, 15, True)


def test_estrutura_faixa_de_peso_rejeita_igual_cotar():
    from frete import faixa_de_peso

    for peso in (0, -5, 30001):
        with pytest.raises(ValueError):
            faixa_de_peso(peso)
    for peso in (True, False, 10.0, "300", None):
        with pytest.raises(TypeError):
            faixa_de_peso(peso)
