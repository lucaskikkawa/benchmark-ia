"""Testes de comportamento público de carrinho.calcular_total."""

import importlib
import sys
from pathlib import Path

import pytest

try:
    import carrinho
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    carrinho = importlib.import_module("carrinho")


def _chamar(itens, desconto=0, frete=0):
    copia = list(itens)
    ids_tuplas = [id(item) for item in itens]
    id_lista = id(itens)
    resultado = carrinho.calcular_total(itens, desconto=desconto, frete=frete)
    assert type(resultado) is int
    assert id(itens) == id_lista
    assert [id(item) for item in itens] == ids_tuplas
    assert itens == copia
    return resultado


def _erro(itens, desconto=0, frete=0):
    copia = list(itens)
    ids_tuplas = [id(item) for item in itens]
    id_lista = id(itens)
    with pytest.raises(ValueError):
        carrinho.calcular_total(itens, desconto=desconto, frete=frete)
    assert id(itens) == id_lista
    assert [id(item) for item in itens] == ids_tuplas
    assert itens == copia


@pytest.mark.parametrize(
    "itens,desconto,frete,esperado",
    [
        ([], 0, 0, 0),
        ([], 0, 50, 0),
        ([], 100, 99, 0),
        ([], 15, 1, 0),
        ([(0, 0)], 0, 0, 0),
        ([(0, 0)], 10, 50, 0),
        ([(0, 100)], 0, 50, 0),
        ([(0, 100)], 10, 50, 0),
        ([(0, 0), (0, 500)], 20, 50, 0),
        ([(0, 10**18)], 0, 10**9, 0),
        ([(1, 0)], 0, 0, 0),
        ([(1, 0)], 0, 50, 50),
        ([(5, 0)], 10, 50, 50),
        ([(5, 0)], 100, 50, 50),
        ([(1, 0), (2, 0)], 100, 8, 8),
        ([(2, 0), (3, 0)], 0, 11, 11),
        ([(0, 100), (1, 0), (0, 5)], 40, 15, 15),
        ([(0, 500), (2, 40)], 10, 9, 81),
        ([(1, 100)], 0, 0, 100),
        ([(1, 40)], 0, 0, 40),
        ([(1, 250)], 0, 0, 250),
        ([(2, 50)], 0, 0, 100),
        ([(2, 50), (3, 10)], 0, 0, 130),
        ([(4, 100)], 0, 7, 407),
        ([(1, 100), (1, 100)], 0, 7, 207),
        ([(3, 100), (0, 999)], 0, 7, 307),
        ([(1, 100), (0, 0), (1, 50)], 0, 4, 154),
        ([(1, 100), (0, 50)], 0, 9, 109),
        ([(3, 10), (0, 5)], 0, 4, 34),
        ([(0, 5), (3, 10)], 0, 4, 34),
        ([(0, 10**100), (1, 1)], 0, 0, 1),
        ([(1, 200)], 10, 0, 180),
        ([(1, 250)], 10, 0, 225),
        ([(1, 100)], 10, 50, 140),
        ([(1, 100)], 10, 0, 90),
        ([(4, 100)], 10, 7, 367),
        ([(1, 7)], 100, 0, 0),
        ([(1, 7)], 100, 4, 4),
        ([(2, 80)], 100, 12, 12),
        ([(0, 80)], 100, 12, 0),
        ([(2, 80)], 0, 12, 172),
        ([(1, 10**30)], 0, 10**30, 2 * 10**30),
        ([(1, 1)], 1, 0, 0),
        ([(1, 1)], 50, 0, 0),
        ([(1, 3)], 50, 0, 1),
        ([(2, 1)], 50, 0, 1),
        ([(3, 1)], 50, 0, 1),
        ([(7, 1)], 1, 0, 6),
        ([(3, 10)], 15, 0, 25),
        ([(100, 1)], 50, 3, 53),
        ([(1, 101)], 1, 0, 99),
        ([(1, 101)], 99, 0, 1),
        ([(1, 999)], 7, 0, 929),
        ([(1, 10), (1, 10)], 15, 0, 17),
        ([(1, 10), (1, 10)], 15, 5, 22),
        ([(1, 33), (1, 33), (1, 33)], 10, 0, 89),
        ([(1, 50), (1, 50), (1, 50)], 1, 0, 148),
        ([(1, 10)] * 10, 15, 1, 86),
        ([(2, 100), (3, 0)], 25, 10, 160),
        ([(1, 200), (2, 30)], 10, 7, 241),
        (
            [(2, 1500), (1, 990), (0, 10), (4, 25), (1, 0)],
            12,
            350,
            3949,
        ),
        ([(1, 2**53 + 3)], 0, 0, 9007199254740995),
        ([(3, 2**53 + 3)], 0, 0, 27021597764222985),
        ([(1, 10**18 + 17)], 1, 0, 990000000000000016),
        ([(1, 2**60)], 1, 1, 1141392289560778507),
        ([(1, 2**53 + 3)], 50, 0, 4503599627370497),
        (
            [(10**12, 10**12), (1, 1)],
            0,
            10**12,
            10**24 + 10**12 + 1,
        ),
    ],
)
def test_totais(itens, desconto, frete, esperado):
    assert _chamar(list(itens), desconto, frete) == esperado


def test_cem_linhas_de_um_centavo_truncam_no_agregado():
    itens = [(1, 1)] * 100
    assert _chamar(itens, desconto=50, frete=3) == 53


def test_argumentos_padrao_e_nomeados():
    itens = [(1, 250)]
    assert carrinho.calcular_total(itens) == 250
    assert type(carrinho.calcular_total(itens)) is int
    assert carrinho.calcular_total(itens, 0) == 250
    assert carrinho.calcular_total(itens, 0, 0) == 250
    assert carrinho.calcular_total(itens, desconto=0) == 250
    assert carrinho.calcular_total(itens, frete=0) == 250
    assert carrinho.calcular_total(itens, desconto=0, frete=0) == 250
    assert carrinho.calcular_total(itens, frete=20) == 270
    assert carrinho.calcular_total(itens, desconto=10) == 225
    assert carrinho.calcular_total(itens, frete=20, desconto=10) == 245
    assert carrinho.calcular_total([(1, 200), (2, 30)], 10, 7) == 241
    assert itens == [(1, 250)]


def test_desconto_zero_e_cem_nao_levantam():
    assert _chamar([(4, 25), (1, 0)], desconto=0, frete=0) == 100
    assert _chamar([(4, 25)], desconto=100, frete=0) == 0
    assert _chamar([(4, 25)], desconto=100, frete=6) == 6
    assert _chamar([(0, 25)], desconto=100, frete=6) == 0


def test_frete_zero_com_itens_pagos():
    assert _chamar([(2, 80), (1, 15)], desconto=0, frete=0) == 175
    assert _chamar([(2, 80), (1, 15)], desconto=10, frete=0) == 157


def test_chamadas_independentes_e_lista_reutilizada():
    itens = [(2, 10), (1, 50)]
    assert _chamar(itens, desconto=15, frete=5) == 64
    assert _chamar(itens, desconto=0, frete=0) == 70
    assert _chamar(itens, desconto=100, frete=9) == 9
    assert carrinho.calcular_total([(1, 100)], 50) == 50
    assert carrinho.calcular_total([(1, 100)], 10) == 90
    assert carrinho.calcular_total([(1, 100)]) == 100
    for _ in range(30):
        assert carrinho.calcular_total([(2, 25)], 10, 3) == 48
        assert carrinho.calcular_total([], frete=10) == 0
    assert itens == [(2, 10), (1, 50)]


def test_lista_nao_e_reordenada():
    a, b, c = (2, 10), (1, 50), (2, 1)
    itens = [a, b, c]
    assert _chamar(itens, desconto=5, frete=2) == 70
    assert itens[0] is a and itens[1] is b and itens[2] is c


def test_lista_intacta_quando_desconto_invalido():
    a, b, c = (2, 5), (1, 9), (3, 1)
    itens = [a, b, c]
    _erro(itens, desconto=-1, frete=0)
    _erro(itens, desconto=101, frete=4)
    assert itens[0] is a and itens[1] is b and itens[2] is c


def test_lista_intacta_quando_frete_invalido():
    a, b = (1, 10), (4, 1)
    itens = [a, b]
    _erro(itens, desconto=0, frete=-1)
    assert itens[0] is a and itens[1] is b


def test_lista_intacta_quando_item_invalido_no_meio():
    a, b, c = (1, 10), (-1, 5), (2, 8)
    itens = [a, b, c]
    _erro(itens, desconto=10, frete=3)
    assert itens == [a, b, c]
    assert itens[0] is a and itens[1] is b and itens[2] is c


def test_erro_nao_contamina_a_chamada_seguinte():
    itens = [(1, 100), (0, -1)]
    _erro(itens, desconto=10, frete=5)
    itens[1] = (0, 50)
    assert _chamar(itens, desconto=10, frete=5) == 95
    assert carrinho.calcular_total([(1, 80)]) == 80
    assert carrinho.calcular_total([]) == 0


@pytest.mark.parametrize(
    "itens",
    [
        [],
        [(0, 0)],
        [(0, 10)],
        [(1, 10)],
        [(1, 0)],
        [(2, 5), (0, 1)],
    ],
)
@pytest.mark.parametrize("desconto", [-1, -100, 101, 10**6])
def test_desconto_fora_da_faixa(itens, desconto):
    _erro(list(itens), desconto=desconto, frete=0)
    _erro(list(itens), desconto=desconto, frete=10)


@pytest.mark.parametrize(
    "itens",
    [
        [],
        [(0, 0)],
        [(0, 10)],
        [(1, 10)],
        [(1, 0)],
        [(2, 5), (0, 1)],
    ],
)
@pytest.mark.parametrize("frete", [-1, -100, -(10**18)])
def test_frete_negativo(itens, frete):
    _erro(list(itens), desconto=0, frete=frete)
    _erro(list(itens), desconto=100, frete=frete)
    _erro(list(itens), desconto=10, frete=frete)


@pytest.mark.parametrize(
    "itens",
    [
        [(-1, 0)],
        [(-1, 10)],
        [(-1, -1)],
        [(0, -1)],
        [(1, -1)],
        [(0, 0), (-1, 0)],
        [(0, 10), (1, -1)],
        [(0, 10), (-1, 10)],
        [(0, -1), (1, 10)],
        [(1, 10), (0, -1)],
        [(1, 10), (-2, 3)],
        [(1, 10), (2, -3)],
        [(2, 10), (0, 0), (0, -5)],
        [(-10**18, 1)],
        [(1, -(10**18))],
        [(0, 10**18), (-1, 1)],
        [(1, 10), (0, 1), (0, 2), (3, -1)],
        [(0, 0), (0, 0), (0, -1)],
        [(0, 1), (1, 2), (1, -3)],
        [(5, 5), (0, -8), (1, 1)],
        [(0, 0), (0, -1), (0, 0)],
    ],
)
def test_linha_invalida_preserva_a_lista(itens):
    _erro(list(itens), desconto=0, frete=0)
    _erro(list(itens), desconto=15, frete=4)


def test_quantidade_zero_e_preco_zero_sao_validos():
    assert _chamar([(0, 0), (0, 0)], 0, 0) == 0
    assert _chamar([(0, 0)], desconto=100, frete=1) == 0
    assert _chamar([(6, 0)], desconto=0, frete=1) == 1
