import copy
import random

import pytest

from intervalos import mesclar_intervalos, total_coberto


def forca_bruta(intervalos):
    """Oráculo simples: une repetidamente até estabilizar."""
    blocos = sorted(tuple(i) for i in intervalos)
    resultado = []
    for inicio, fim in blocos:
        if resultado and inicio <= resultado[-1][1]:
            resultado[-1] = (resultado[-1][0], max(resultado[-1][1], fim))
        else:
            resultado.append((inicio, fim))
    return resultado


def test_lista_vazia():
    assert mesclar_intervalos([]) == []
    assert total_coberto([]) == 0


def test_casos_basicos():
    assert mesclar_intervalos([(2, 4)]) == [(2, 4)]
    assert mesclar_intervalos([(1, 2), (4, 5), (7, 9)]) == [(1, 2), (4, 5), (7, 9)]
    assert mesclar_intervalos([(1, 4), (2, 6)]) == [(1, 6)]


def test_entrada_fora_de_ordem():
    assert mesclar_intervalos([(5, 7), (1, 3)]) == [(1, 3), (5, 7)]
    assert mesclar_intervalos([(8, 10), (1, 3), (2, 6)]) == [(1, 6), (8, 10)]


def test_intervalos_que_se_tocam():
    assert mesclar_intervalos([(1, 3), (3, 6)]) == [(1, 6)]
    assert mesclar_intervalos([(3, 6), (1, 3)]) == [(1, 6)]


def test_intervalo_contido_nao_encolhe():
    assert mesclar_intervalos([(1, 10), (2, 3), (4, 5)]) == [(1, 10)]
    assert mesclar_intervalos([(4, 5), (1, 10), (2, 3), (11, 12)]) == [(1, 10), (11, 12)]


def test_intervalos_degenerados_iguais_e_negativos():
    assert mesclar_intervalos([(3, 3), (3, 3)]) == [(3, 3)]
    assert mesclar_intervalos([(1, 2), (2, 2), (5, 5)]) == [(1, 2), (5, 5)]
    assert mesclar_intervalos([(-5, -1), (-2, 0), (2, 3)]) == [(-5, 0), (2, 3)]


def test_inteiros_grandes():
    g = 10**30
    assert mesclar_intervalos([(g, g + 5), (-g, g)]) == [(-g, g + 5)]
    assert total_coberto([(g, g + 5), (-g, g)]) == 2 * g + 5


def test_nao_modifica_lista_de_entrada():
    entrada = [(5, 7), (1, 3), (2, 4)]
    original = copy.deepcopy(entrada)
    mesclar_intervalos(entrada)
    assert entrada == original
    total_coberto(entrada)
    assert entrada == original


def test_nao_modifica_pares_em_lista():
    entrada = [[5, 7], [1, 3], [2, 4], [6, 9]]
    original = copy.deepcopy(entrada)
    assert mesclar_intervalos(entrada) == [(1, 4), (5, 9)]
    assert entrada == original


def test_retorna_nova_lista_de_tuplas():
    entrada = [(1, 2)]
    resultado = mesclar_intervalos(entrada)
    assert resultado == [(1, 2)] and resultado is not entrada
    resultado = mesclar_intervalos([[4, 5], [1, 2]])
    assert isinstance(resultado, list)
    assert all(type(i) is tuple for i in resultado)


def test_aceita_tupla_de_intervalos():
    assert mesclar_intervalos(((5, 7), (1, 3), (3, 4))) == [(1, 4), (5, 7)]
    assert total_coberto(((5, 7), (1, 3), (3, 4))) == 5


def test_aceita_gerador():
    gerador = ((i, i + 2) for i in (10, 0, 1, 20))
    assert mesclar_intervalos(gerador) == [(0, 3), (10, 12), (20, 22)]


def test_total_coberto_aceita_gerador():
    assert total_coberto((i, i + 1) for i in range(0, 10, 3)) == 4


def test_gerador_com_intervalo_invalido():
    with pytest.raises(ValueError):
        mesclar_intervalos(iter([(1, 2), (9, 3)]))


def test_intervalo_invalido():
    with pytest.raises(ValueError):
        mesclar_intervalos([(1, 2), (5, 3)])
    with pytest.raises(ValueError):
        total_coberto([(2, 1)])


def test_intervalo_invalido_mesmo_se_contido_em_outro():
    with pytest.raises(ValueError):
        mesclar_intervalos([(0, 100), (50, 40)])


@pytest.mark.parametrize(
    "intervalos",
    [
        [(1, 2), (1.0, 3)],
        [(1, 2.5)],
        [("1", "3")],
        [(None, 3)],
        [(True, 3)],
        [(0, False)],
    ],
    ids=["float_inicio", "float_fim", "str", "none", "bool_inicio", "bool_fim"],
)
def test_tipos_invalidos_levantam_type_error(intervalos):
    with pytest.raises(TypeError):
        mesclar_intervalos(intervalos)


def test_total_coberto_tipo_invalido():
    with pytest.raises(TypeError):
        total_coberto([(0, 1), (2, 3.0)])


def test_total_coberto_com_sobreposicao_e_contido():
    assert total_coberto([(1, 3), (2, 6), (8, 9)]) == 6
    assert total_coberto([(4, 5), (0, 10), (12, 13)]) == 11
    assert total_coberto([(0, 5), (5, 5), (5, 8)]) == 8


def test_aleatorio_contra_oraculo():
    rng = random.Random(42)
    for _ in range(500):
        n = rng.randint(0, 12)
        intervalos = []
        for _ in range(n):
            a = rng.randint(-20, 20)
            intervalos.append((a, a + rng.randint(0, 8)))
        esperado = forca_bruta(intervalos)
        assert mesclar_intervalos(intervalos) == esperado, intervalos
        assert total_coberto(intervalos) == sum(f - i for i, f in esperado)


def test_entrada_grande():
    rng = random.Random(7)
    intervalos = []
    for _ in range(200_000):
        a = rng.randint(-10**9, 10**9)
        intervalos.append((a, a + rng.randint(0, 5_000)))
    copia = list(intervalos)
    obtido = mesclar_intervalos(intervalos)
    esperado = forca_bruta(copia)
    # Fora do assert: o diff do pytest em ~1e5 tuplas trava a suíte por minutos.
    if intervalos != copia:
        pytest.fail("a entrada foi modificada")
    if obtido != esperado:
        for indice, (a, b) in enumerate(zip(obtido, esperado)):
            if a != b:
                pytest.fail(f"divergiu no índice {indice}: {a} != {b} (len {len(obtido)} vs {len(esperado)})")
        pytest.fail(f"tamanhos diferentes: {len(obtido)} vs {len(esperado)}")
