import pytest
from janelas import somas_janelas


def test_ultima_janela():
    assert somas_janelas([1, 2, 3, 4], 2) == [3, 5, 7]


def test_unitarias():
    assert somas_janelas([5, -2, 9], 1) == [5, -2, 9]


def test_tamanho_total():
    assert somas_janelas([2, 4, 6], 3) == [12]


def test_vazia():
    assert somas_janelas([], 1) == []


def test_maior():
    assert somas_janelas([1, 2], 3) == []


def test_um_elemento():
    assert somas_janelas([7], 1) == [7]


def test_zeros():
    assert somas_janelas([0, 0, 0, 0], 2) == [0, 0, 0]


def test_negativos():
    assert somas_janelas([-3, 4, -8, 2, 9], 3) == [-7, -2, 3]


def test_sem_mutacao():
    dados = [8, 3, 1]
    assert somas_janelas(dados, 2) == [11, 4]
    assert dados == [8, 3, 1]


@pytest.mark.parametrize('tamanho', [0, -1, -10])
def test_tamanho_invalido(tamanho):
    with pytest.raises(ValueError):
        somas_janelas([], tamanho)
