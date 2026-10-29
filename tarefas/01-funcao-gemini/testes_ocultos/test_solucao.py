import pytest
from solucao import resumir_intervalos


def test_lista_vazia():
    assert resumir_intervalos([]) == ""


def test_elemento_unico():
    assert resumir_intervalos([42]) == "42"


def test_dois_elementos_consecutivos():
    assert resumir_intervalos([7, 8]) == "7-8"


def test_dois_elementos_nao_consecutivos():
    assert resumir_intervalos([7, 9]) == "7, 9"


def test_intervalos_multiplos():
    assert resumir_intervalos([1, 2, 3, 5, 7, 8, 9]) == "1-3, 5, 7-9"


def test_desordenado_com_duplicatas():
    assert resumir_intervalos([9, 1, 8, 2, 7, 3, 5, 2, 1, 8]) == "1-3, 5, 7-9"


def test_numeros_negativos():
    assert resumir_intervalos([-3, -2, -1, 1, 2]) == "-3--1, 1-2"


def test_transicao_negativo_para_positivo():
    assert resumir_intervalos([-2, -1, 0, 1, 2]) == "-2-2"


def test_todos_isolados():
    assert resumir_intervalos([10, 20, 30, 40]) == "10, 20, 30, 40"


def test_grande_intervalo_continuo():
    assert resumir_intervalos(list(range(1, 101))) == "1-100"


def test_tipo_invalido_na_lista():
    with pytest.raises(TypeError):
        resumir_intervalos([1, 2, "3", 4])
    with pytest.raises(TypeError):
        resumir_intervalos([1, 2.5, 3])
    with pytest.raises(TypeError):
        resumir_intervalos([1, True, 3])


def test_entrada_nao_lista():
    with pytest.raises(TypeError):
        resumir_intervalos("1, 2, 3")  # type: ignore
    with pytest.raises(TypeError):
        resumir_intervalos(None)  # type: ignore


def test_apenas_duplicatas():
    assert resumir_intervalos([0, 0, 0]) == "0"


def test_inteiros_sem_limite_de_32_ou_64_bits():
    n = 10**30
    assert resumir_intervalos([n + 1, -n, n]) == f"{-n}, {n}-{n + 1}"


@pytest.mark.parametrize("entrada", [(1, 2), {1, 2}, 123, {}])
def test_outros_containers_nao_sao_listas(entrada):
    with pytest.raises(TypeError):
        resumir_intervalos(entrada)


@pytest.mark.parametrize("elemento", [False, None, [2], 2.0])
def test_elementos_estritamente_inteiros(elemento):
    with pytest.raises(TypeError):
        resumir_intervalos([1, elemento, 3])
