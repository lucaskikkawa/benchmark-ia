"""Recorte, precisão e varredura comparada a eventos de extremidades."""
from copy import deepcopy
import random
import pytest
from solucao import unir_intervalos


def por_eventos(intervalos, limites=None):
    eventos = []
    for inicio, fim in intervalos:
        if limites is not None:
            inicio, fim = max(inicio, limites[0]), min(fim, limites[1])
        if inicio <= fim:
            # Inícios antes dos fins no mesmo ponto: intervalos fechados se unem.
            eventos.extend([(inicio, -1), (fim, 1)])
    ativos, resultado = 0, []
    for coordenada, evento in sorted(eventos):
        if ativos == 0:
            inicio = coordenada
        ativos -= evento
        if ativos == 0:
            resultado.append((inicio, coordenada))
    return resultado


@pytest.mark.parametrize('limites,esperado', [
    ((0, 0), [(0, 0)]), ((-3, 2), [(-3, 2)]),
    ((-8, -6), [(-8, -6)]), ((20, 40), []),
    ((9, 10), [(9, 9), (10, 10)]),
])
def test_recorte_fechado(limites, esperado):
    dados = [[10, 12], [-10, -2], [-2, 3], [7, 9]]
    antes, bordas = deepcopy(dados), list(limites)
    assert unir_intervalos((par for par in dados), limites=bordas) == esperado
    assert dados == antes and bordas == list(limites)


@pytest.mark.parametrize('dados,limites', [
    ([], (1, -1)), ([(0, 5)], (3, 2)),
    ([(0, 0), (100, 99)], (-1, 1)),
    ([(-100, -101), (0, 0)], (0, 0)),
])
def test_invertidos_nao_desaparecem_no_recorte(dados, limites):
    with pytest.raises(ValueError):
        unir_intervalos(iter(dados), limites=limites)


def test_precisao_entre_inteiros_vizinhos_enormes():
    base = 10**120
    dados = [(base + 3, base + 4), (base, base + 2),
             (-base, -base + 1), (-base + 2, -base + 2)]
    esperado = sorted(dados)
    resultado = unir_intervalos(dados)
    assert type(resultado) is list
    assert all(type(par) is tuple for par in resultado)
    assert resultado == esperado
    assert unir_intervalos(dados, limites=(base + 2, base + 3)) == [
        (base + 2, base + 2), (base + 3, base + 3)]


def test_oraculo_semente_fixa_e_idempotencia():
    rng = random.Random(7901)
    for _ in range(100):
        dados = [tuple(sorted((rng.randrange(-30, 31), rng.randrange(-30, 31))))
                 for _ in range(rng.randrange(45))]
        limites = tuple(sorted((rng.randrange(-35, 36), rng.randrange(-35, 36))))
        for recorte in (None, limites):
            esperado = por_eventos(dados, recorte)
            assert unir_intervalos((par for par in dados), limites=recorte) == esperado
            assert unir_intervalos(esperado, limites=recorte) == esperado


def test_volume_contidos_nao_encurtam_limite():
    dados = [(4*i, 4*i + 2) for i in reversed(range(30_000))]
    dados.extend([(4*i + 1, 4*i + 1) for i in range(30_000)])
    assert unir_intervalos(dados) == [(4*i, 4*i + 2) for i in range(30_000)]
    # Um intervalo abrangente que aparece por último une todas as componentes.
    dados.append((0, 120_000))
    assert unir_intervalos(iter(dados)) == [(0, 120_000)]


def test_vazio_recortado_e_chamadas_independentes():
    assert unir_intervalos(iter(()), limites=(0, 0)) == []
    primeiro = unir_intervalos([[2, 8]])
    primeiro.append((90, 100))
    assert unir_intervalos([], limites=(-2, 2)) == []
    assert unir_intervalos([(2, 8)]) == [(2, 8)]
