"""Comportamento público de carrinho.calcular_total."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from carrinho import calcular_total


def test_carrinho_vazio_sem_desconto_nem_frete():
    assert calcular_total([]) == 0


def test_carrinho_vazio_ignora_frete_e_desconto_validos():
    assert calcular_total([], desconto=0, frete=0) == 0
    assert calcular_total([], desconto=100, frete=999) == 0
    assert calcular_total([], 40, 15) == 0


def test_quantidade_zero_nao_cobra_frete():
    assert calcular_total([(0, 500)], frete=80) == 0
    assert calcular_total([(0, 0), (0, 10_000)], desconto=15, frete=80) == 0


def test_item_gratuito_com_quantidade_positiva_cobra_frete():
    assert calcular_total([(1, 0)], frete=80) == 80
    assert calcular_total([(4, 0)], desconto=100, frete=8) == 8
    assert calcular_total([(0, 50), (3, 0)], desconto=25, frete=9) == 9


def test_frete_nao_entra_no_desconto():
    assert calcular_total([(1, 100)], desconto=50, frete=10) == 60
    assert calcular_total([(2, 100), (1, 100)], desconto=50, frete=5) == 155


def test_frete_uma_vez_com_varias_linhas_e_unidades():
    assert calcular_total([(2, 100)], frete=5) == 205
    assert calcular_total([(1, 100), (1, 100)], frete=5) == 205
    assert calcular_total([(1, 100), (0, 1)], frete=7) == 107
    assert calcular_total([(0, 1), (1, 100)], frete=5) == 105


def test_desconto_zero_e_cem_inclusive():
    assert calcular_total([(3, 40)], desconto=0, frete=0) == 120
    assert calcular_total([(5, 20)], desconto=100, frete=7) == 7
    assert calcular_total([(5, 20), (0, 9)], desconto=100, frete=0) == 0
    assert calcular_total([(101, 1)], desconto=0) == 101


def test_desconto_trunca_para_baixo_no_bruto_agregado():
    assert calcular_total([(1, 10)], desconto=33) == 6
    assert calcular_total([(1, 1)], desconto=1) == 0
    assert calcular_total([(1, 1)], desconto=40) == 0
    assert calcular_total([(1, 15)], desconto=50) == 7
    assert calcular_total([(1, 150)], desconto=10) == 135
    assert calcular_total([(1, 100)], desconto=10) == 90
    assert calcular_total([(1, 99)], desconto=100) == 0
    assert calcular_total([(1, 1)], desconto=99) == 0
    assert calcular_total([(1, 100)], desconto=99) == 1


def test_truncamento_agregado_difere_da_soma_por_linha():
    assert calcular_total([(1, 1), (1, 1)], desconto=50) == 1
    assert calcular_total([(1, 1), (1, 1), (1, 1)], desconto=50) == 1
    assert calcular_total([(1, 1)] * 10, desconto=33) == 6
    assert calcular_total([(2, 150), (3, 200)], desconto=10, frete=20) == 830


def test_linha_zero_no_meio_nao_interrompe_a_soma():
    assert calcular_total([(1, 100), (0, 0), (1, 50)]) == 150
    assert calcular_total([(1, 100), (0, 50), (1, 100)], frete=5) == 205
    assert calcular_total([(2, 10), (0, 999), (1, 5)], desconto=25, frete=9) == 27


def test_preco_e_quantidade_zero_sao_validos():
    assert calcular_total([(0, 0)]) == 0
    assert calcular_total([(2, 5)]) == 10
    assert calcular_total([(100, 1)], desconto=3) == 97


def test_inteiros_grandes_exatos():
    preco = 2**53 + 3
    assert calcular_total([(1, preco)]) == preco
    assert calcular_total([(2**53, 1), (3, 1)]) == 2**53 + 3
    bruto = 10**36
    assert calcular_total([(10**18, 10**18)], desconto=1, frete=10**18) == (
        bruto * 99 // 100 + 10**18
    )
    assert calcular_total([(1, 2**63)], desconto=0, frete=2**63) == 2**63 + 2**63
    assert type(calcular_total([(1, 2**60)], desconto=1)) is int


def test_chamadas_independentes_e_argumentos_nomeados():
    assert calcular_total([(1, 100)], desconto=10) == 90
    assert calcular_total([(1, 100)], desconto=10) == 90
    assert calcular_total([(1, 50)]) == 50
    assert calcular_total([(1, 10)]) == 10
    assert calcular_total([(1, 10), (1, 10)]) == 20
    assert calcular_total(itens=[(4, 25)], desconto=20, frete=3) == 83


def test_lista_intacta_no_sucesso():
    item = (2, 50)
    itens = [item, (1, 5), (0, 9)]
    original = [(2, 50), (1, 5), (0, 9)]
    assert calcular_total(itens, desconto=10, frete=3) == 97
    assert itens == original
    assert itens[0] is item
    assert calcular_total(itens, desconto=10, frete=3) == 97
    assert itens == original


@pytest.mark.parametrize(
    "kwargs",
    [
        {"desconto": -1},
        {"desconto": 101},
        {"desconto": -5, "frete": 10},
        {"desconto": 150},
        {"frete": -1},
        {"frete": -100, "desconto": 0},
    ],
)
def test_faixa_de_desconto_e_frete(kwargs):
    itens = [(1, 100), (2, 50)]
    snapshot = list(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, **kwargs)
    assert itens == snapshot
    with pytest.raises(ValueError):
        calcular_total([], **kwargs)


@pytest.mark.parametrize(
    "itens",
    [
        [(-1, 100)],
        [(1, -1)],
        [(0, -1)],
        [(-1, -1)],
        [(1, 100), (-1, 50)],
        [(1, 100), (1, -5)],
        [(0, 100), (-1, 100)],
        [(0, 100), (1, -5)],
        [(0, -5), (1, 100)],
        [(1, 100), (0, -1)],
        [(2, 30), (0, 0), (-1, 1)],
        [(0, 10), (0, 10), (3, -1)],
        [(-5, 0)],
        [(1, 0), (0, -8)],
    ],
)
def test_quantidade_ou_preco_negativo(itens):
    snapshot = [tuple(par) for par in itens]
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=10, frete=5)
    assert itens == snapshot
    assert [tuple(par) for par in itens] == snapshot


def test_lista_intacta_quando_desconto_invalido_em_carrinho_vazio_ou_zerado():
    vazio = []
    with pytest.raises(ValueError):
        calcular_total(vazio, desconto=-1, frete=4)
    assert vazio == []

    zeros = [(0, 100), (0, 0)]
    with pytest.raises(ValueError):
        calcular_total(zeros, desconto=101, frete=4)
    assert zeros == [(0, 100), (0, 0)]

    with pytest.raises(ValueError):
        calcular_total(zeros, frete=-1)
    assert zeros == [(0, 100), (0, 0)]


def test_erro_nao_contamina_a_chamada_seguinte():
    itens = [(1, 200), (0, 1), (-2, 5)]
    snapshot = list(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=50, frete=12)
    assert itens == snapshot
    assert calcular_total([(1, 200)], desconto=50, frete=12) == 112
    assert calcular_total(snapshot[:2], desconto=50, frete=12) == 112
