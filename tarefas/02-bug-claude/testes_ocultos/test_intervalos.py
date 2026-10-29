import copy

import pytest

from intervalos import mesclar_intervalos, total_coberto


def test_lista_vazia():
    assert mesclar_intervalos([]) == []


def test_total_lista_vazia():
    assert total_coberto([]) == 0


def test_um_intervalo():
    assert mesclar_intervalos([(2, 4)]) == [(2, 4)]


def test_disjuntos_ja_ordenados():
    assert mesclar_intervalos([(1, 2), (4, 5), (7, 9)]) == [(1, 2), (4, 5), (7, 9)]


def test_sobreposicao_simples():
    assert mesclar_intervalos([(1, 4), (2, 6)]) == [(1, 6)]


def test_entrada_fora_de_ordem():
    assert mesclar_intervalos([(5, 7), (1, 3)]) == [(1, 3), (5, 7)]
    assert mesclar_intervalos([(8, 10), (1, 3), (2, 6)]) == [(1, 6), (8, 10)]


def test_intervalos_que_se_tocam():
    assert mesclar_intervalos([(1, 3), (3, 6)]) == [(1, 6)]


def test_intervalo_contido_nao_encolhe():
    assert mesclar_intervalos([(1, 10), (2, 3), (4, 5)]) == [(1, 10)]


def test_intervalos_degenerados_e_iguais():
    assert mesclar_intervalos([(3, 3), (3, 3)]) == [(3, 3)]
    assert mesclar_intervalos([(1, 2), (2, 2), (5, 5)]) == [(1, 2), (5, 5)]


def test_negativos():
    assert mesclar_intervalos([(-5, -1), (-2, 0), (2, 3)]) == [(-5, 0), (2, 3)]


def test_nao_modifica_entrada():
    entrada = [(5, 7), (1, 3), (2, 4)]
    original = copy.deepcopy(entrada)
    mesclar_intervalos(entrada)
    assert entrada == original


def test_retorna_lista_de_tuplas():
    resultado = mesclar_intervalos([(4, 5), (1, 2)])
    assert isinstance(resultado, list)
    assert all(type(i) is tuple for i in resultado)


def test_intervalo_invalido():
    with pytest.raises(ValueError):
        mesclar_intervalos([(1, 2), (5, 3)])
    with pytest.raises(ValueError):
        total_coberto([(2, 1)])


def test_total_coberto_com_sobreposicao():
    assert total_coberto([(1, 3), (2, 6), (8, 9)]) == 6


def test_total_coberto_fora_de_ordem_e_contido():
    assert total_coberto([(4, 5), (0, 10), (12, 13)]) == 11
