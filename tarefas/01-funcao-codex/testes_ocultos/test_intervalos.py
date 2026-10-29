import pytest
from solucao import unir_intervalos


def test_vazio():
    assert unir_intervalos([]) == []


def test_ponto():
    assert unir_intervalos([(4, 4)]) == [(4, 4)]


def test_exemplo():
    assert unir_intervalos([(5, 8), (1, 3), (3, 6), (10, 10)]) == [(1, 8), (10, 10)]


def test_adjacentes_sem_extremidade_comum():
    assert unir_intervalos([(3, 4), (1, 2)]) == [(1, 2), (3, 4)]


def test_contidos_e_duplicados():
    assert unir_intervalos([(0, 10), (2, 3), (0, 10), (8, 9)]) == [(0, 10)]


def test_negativos_e_pontos():
    assert unir_intervalos([(-3, -1), (-8, -3), (0, 0)]) == [(-8, -1), (0, 0)]


def test_cadeia_e_mesmo_inicio():
    assert unir_intervalos([(2, 2), (2, 5), (8, 9), (5, 8)]) == [(2, 9)]


def test_gerador():
    assert unir_intervalos((x for x in [(9, 10), (1, 2)])) == [(1, 2), (9, 10)]


def test_nao_altera_listas():
    dados = [[7, 9], [1, 2], [2, 5]]
    assert unir_intervalos(dados) == [(1, 5), (7, 9)]
    assert dados == [[7, 9], [1, 2], [2, 5]]


@pytest.mark.parametrize('dados', [[(2, 1)], [(0, 9), (5, 4)], [(3, -3)]])
def test_invertido(dados):
    with pytest.raises(ValueError):
        unir_intervalos(iter(dados))
