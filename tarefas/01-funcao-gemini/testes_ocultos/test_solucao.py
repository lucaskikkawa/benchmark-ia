from collections import deque
import pytest
from solucao import resumir_intervalos


class IntSubclasse(int):
    pass


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


@pytest.mark.parametrize("entrada", [(1, 2), {1, 2}, 123, {}, deque([1, 2]), range(5)])
def test_outros_containers_nao_sao_listas(entrada):
    with pytest.raises(TypeError):
        resumir_intervalos(entrada)


@pytest.mark.parametrize("elemento", [False, True, None, [2], 2.0, (1,), "1", 1.0])
def test_elementos_estritamente_inteiros(elemento):
    with pytest.raises(TypeError):
        resumir_intervalos([1, elemento, 3])


def test_rejeita_subclasses_personalizadas_de_int():
    custom_int = IntSubclasse(10)
    with pytest.raises(TypeError):
        resumir_intervalos([1, 2, custom_int, 4])


def test_nao_muta_lista_original():
    original = [5, 3, 1, 4, 2]
    copia = list(original)
    resultado = resumir_intervalos(original)
    assert resultado == "1-5"
    assert original == copia, "A função modificou a lista recebida como argumento!"


def test_grande_volume_de_dados():
    # Blocos consecutivos, valores isolados e duplicatas, em ordem embaralhada.
    dados = []
    # Bloco 0 a 999
    dados.extend(range(0, 1000))
    # Pares entre 2000 e 6000 (isolados)
    dados.extend(range(2000, 6000, 2))
    # Bloco 10000 a 11000 com duplicatas
    dados.extend(range(10000, 11001))
    dados.extend(range(10000, 10500))
    # Desordena propositalmente
    import random
    rng = random.Random(42)
    rng.shuffle(dados)

    res = resumir_intervalos(dados)
    esperado = ", ".join(["0-999", *map(str, range(2000, 6000, 2)), "10000-11000"])
    assert res == esperado


def test_apenas_negativos_consecutivos_e_isolados():
    assert resumir_intervalos([-10, -9, -5, -4, -3, -1]) == "-10--9, -5--3, -1"


def test_repeticao_massiva_mesmo_elemento():
    assert resumir_intervalos([-7] * 5000) == "-7"
