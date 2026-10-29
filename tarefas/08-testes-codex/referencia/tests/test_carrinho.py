from copy import deepcopy
import pytest
from carrinho import calcular_total


def test_vazio_sem_frete():
    assert calcular_total([]) == 0


def test_vazio_nao_cobra_frete():
    assert calcular_total([], frete=37) == 0


def test_quantidades_multiplicam_preco():
    assert calcular_total([(3, 70), (2, 20)]) == 250


def test_desconto_no_bruto_total():
    assert calcular_total([(1, 1), (1, 1)], desconto=50) == 1


def test_trunca_e_nao_arredonda_para_cima():
    assert calcular_total([(1, 101)], desconto=50) == 50


def test_frete_adicionado_depois_do_desconto():
    assert calcular_total([(2, 100)], desconto=25, frete=30) == 180


def test_desconto_cem_ainda_cobra_frete():
    assert calcular_total([(1, 900)], desconto=100, frete=25) == 25


def test_unidade_gratis_cobra_frete():
    assert calcular_total([(1, 0)], frete=20) == 20


def test_quantidade_zero_nao_cobra_frete():
    assert calcular_total([(0, 500), (0, 0)], frete=12) == 0


@pytest.mark.parametrize('desconto', [-1, 101])
def test_desconto_invalido(desconto):
    with pytest.raises(ValueError):
        calcular_total([], desconto=desconto)


def test_frete_negativo():
    with pytest.raises(ValueError):
        calcular_total([], frete=-1)


def test_quantidade_negativa():
    with pytest.raises(ValueError):
        calcular_total([(-1, 10)])


def test_preco_negativo_mesmo_sem_unidades():
    with pytest.raises(ValueError):
        calcular_total([(0, -1)])


def test_nao_altera_itens_e_repeticao_independente():
    itens = [(2, 200), (1, 50)]
    antes = deepcopy(itens)
    assert calcular_total(itens) == 450
    assert itens == antes
    assert calcular_total(itens) == 450
