"""Comportamento público de carrinho.calcular_total.

Os valores esperados estão fixos de propósito: a suíte não reimplementa o cálculo.
"""

import pytest

from carrinho import calcular_total


def _assert_lista_intacta(itens, conteudo, identidades):
    assert itens == conteudo
    assert [id(item) for item in itens] == identidades


def _chama(itens, desconto=0, frete=0):
    conteudo = list(itens)
    identidades = [id(item) for item in itens]
    resultado = calcular_total(itens, desconto, frete)
    _assert_lista_intacta(itens, conteudo, identidades)
    assert type(resultado) is int
    return resultado


def test_carrinho_vazio_ignora_desconto_e_frete():
    assert _chama([], 0, 0) == 0
    assert _chama([], 100, 0) == 0
    assert _chama([], 37, 999) == 0
    assert _chama([], desconto=0, frete=1) == 0


def test_desconto_zero_e_cem_sao_validos():
    assert _chama([(1, 100)], 0, 0) == 100
    assert _chama([(1, 100)], 100, 0) == 0
    assert _chama([(2, 40), (1, 20)], desconto=0, frete=0) == 100
    assert _chama([(2, 40), (1, 20)], desconto=100, frete=0) == 0


def test_frete_zero_e_valido():
    assert _chama([(3, 10)], 0, 0) == 30
    assert _chama([(1, 40)], desconto=25, frete=0) == 30


def test_um_item_quantidade_e_preco_nao_sao_trocados():
    assert _chama([(3, 10)]) == 30
    assert _chama([(10, 3)]) == 30
    assert _chama([(1, 100)]) == 100
    assert _chama([(100, 1)]) == 100


def test_soma_varias_linhas_e_quantidades():
    assert _chama([(2, 100), (3, 50)]) == 350
    assert _chama([(1, 5), (1, 100), (1, 1)]) == 106
    assert _chama([(4, 25), (1, 0), (2, 5)]) == 110


def test_desconto_uma_vez_sobre_o_bruto_e_frete_cheio():
    # 100 com 50% vira 50; frete 10 não entra no desconto.
    assert _chama([(1, 100)], 50, 10) == 60
    # (100 + 10) com 50% seria 55; frete também com 50% seria 55.
    assert _chama([(2, 100)], 10, 7) == 187
    assert _chama([(1, 100), (1, 50)], 0, 7) == 157
    # frete é taxa única, não por unidade nem por linha.
    assert _chama([(2, 100)], 0, 10) == 210
    assert _chama([(5, 20), (4, 20), (1, 20)], 0, 3) == 203


def test_desconto_cem_ainda_cobra_frete_se_houver_unidades():
    assert _chama([(1, 999), (2, 50)], 100, 4) == 4
    assert _chama([(2, 0)], 100, 9) == 9
    assert _chama([(8, 1)], desconto=100, frete=1) == 1


def test_desconto_zero_ainda_cobra_frete():
    assert _chama([(1, 999)], 0, 4) == 1003
    assert _chama([(1, 5)], 0, 2) == 7


def test_truncamento_para_baixo_nao_arredonda():
    # 3 * 50 / 100 = 1.5 → 1 (round half up / round bancário iria a 2).
    assert _chama([(1, 3)], 50, 0) == 1
    # 15 * 90 / 100 = 13.5 → 13.
    assert _chama([(1, 15)], 10, 0) == 13
    # 1 * 99 / 100 = 0.99 → 0. Forma "bruto - bruto*desconto//100" daria 1.
    assert _chama([(1, 1)], 1, 0) == 0
    assert _chama([(1, 199)], 1, 0) == 197


def test_truncamento_agregado_entre_linhas():
    # Por linha: 49 + 49 = 98. No bruto: 100 * 99 // 100 = 99.
    assert _chama([(1, 50), (1, 50)], 1, 0) == 99
    # Por linha: 0 + 0 + 0. No bruto: 3 * 50 // 100 = 1.
    assert _chama([(1, 1), (1, 1), (1, 1)], 50, 0) == 1
    # Três linhas de 10 com 10%: por linha 9+9+9=27; agregado também 27.
    # O caso acima é o que separa as duas regras. Este só soma.
    assert _chama([(1, 10), (1, 10), (1, 10)], 10, 0) == 27


def test_truncamento_agregado_nao_e_por_unidade():
    # Por unidade: (1 * 50 // 100) * 3 = 0. No bruto: 1.
    assert _chama([(3, 1)], 50, 0) == 1
    # Por unidade: (1 * 90 // 100) * 10 = 0. No bruto: 9.
    assert _chama([(10, 1)], 10, 0) == 9
    assert _chama([(3, 1), (10, 1)], 10, 5) == 11 + 5


def test_item_gratuito_com_quantidade_positiva_paga_frete():
    assert _chama([(4, 0)], 0, 8) == 8
    assert _chama([(4, 0)], 50, 8) == 8
    assert _chama([(1, 0)], 0, 1) == 1
    assert _chama([(7, 0), (3, 0)], 15, 4) == 4


def test_linhas_com_quantidade_zero_nao_pagam_frete():
    assert _chama([(0, 100)], 0, 8) == 0
    assert _chama([(0, 100), (0, 50)], 10, 8) == 0
    assert _chama([(0, 0)], 0, 1) == 0
    assert _chama([(0, 10**18)], 50, 12345) == 0


def test_quantidade_zero_nao_zera_o_restante_nem_as_unidades():
    assert _chama([(0, 999), (2, 100)], 10, 5) == 185
    assert _chama([(1, 100), (0, 50), (1, 25)], 0, 0) == 125
    assert _chama([(0, 10), (2, 40)], 0, 3) == 83
    assert _chama([(5, 0), (0, 100)], 0, 3) == 3
    assert _chama([(0, 10), (1, 5), (0, 3)], 0, 2) == 7
    # A última linha não pode substituir a soma das quantidades.
    assert _chama([(5, 10), (0, 1)], 0, 6) == 56
    assert _chama([(0, 1), (5, 10)], 0, 6) == 56


def test_preco_zero_e_quantidade_zero_sao_validos():
    assert _chama([(0, 5)]) == 0
    assert _chama([(1, 0)]) == 0
    assert _chama([(0, 0), (0, 20), (3, 0)]) == 0


def test_inteiros_acima_de_2_elevado_a_53():
    preco = 2**53 + 3
    assert _chama([(1, preco)], 0, 0) == 9007199254740995
    assert _chama([(1, 2**53)], 7, 0) == 8376695306909122
    assert _chama([(1, 2**60)], 1, 0) == 1141392289560778506
    assert _chama([(10**18, 10**18)], 25, 3) == 750000000000000000000000000000000003
    assert _chama([(2**40, 2**40)], 100, 2**40) == 2**40
    assert _chama([(1, 2**53 + 1), (1, 2**53 + 1)], 0, 2**10) == (2**53 + 1) * 2 + 2**10


def test_lista_nao_e_reordenada_nem_reescrita():
    itens = [(1, 5), (1, 100), (0, 7), (2, 3)]
    assert _chama(itens, 10, 4) == 99 + 4
    assert itens == [(1, 5), (1, 100), (0, 7), (2, 3)]


def test_chamadas_sao_independentes():
    itens = [(1, 100), (1, 50)]
    assert _chama(itens, 10, 5) == 140
    assert _chama(itens, 0, 0) == 150
    assert _chama(itens, 100, 8) == 8
    assert _chama(itens, 10, 5) == 140
    outros = [(2, 30)]
    assert _chama(outros, 50, 0) == 30
    assert _chama(itens, 0, 1) == 151


def test_argumentos_nomeados_e_padrao():
    itens = [(2, 15)]
    assert calcular_total(itens) == 30
    assert itens == [(2, 15)]
    assert calcular_total(itens, desconto=0, frete=2) == 32
    assert calcular_total(itens=itens, frete=2, desconto=50) == 17


@pytest.mark.parametrize(
    "itens,desconto,frete",
    [
        ([], -1, 0),
        ([], 101, 0),
        ([], 0, -1),
        ([], -1, -1),
        ([], 10**6, 0),
        ([], 0, -(10**6)),
        ([(0, 10)], -1, 0),
        ([(0, 10)], 101, 0),
        ([(0, 10)], 0, -1),
        ([(0, 0)], 0, -1),
        ([(0, -1)], 0, 0),
        ([(0, -10**9)], 0, 0),
        ([(-1, 0)], 0, 0),
        ([(-10**9, 0)], 0, 0),
        ([(1, -1)], 0, 0),
        ([(1, -10**9)], 0, 0),
        ([(-1, -1)], 0, 0),
        ([(0, 1), (-1, 1)], 0, 0),
        ([(0, 1), (1, -1)], 0, 0),
        ([(0, -5), (1, 10)], 0, 0),
        ([(1, 100), (0, 50), (-2, 25)], 0, 0),
        ([(1, 100), (0, -1)], 0, 0),
        ([(1, 100), (0, 50), (1, -5)], 10, 4),
        ([(2, 5), (-1, 5)], 10, 3),
        ([(1, 1)], 1000, 0),
        ([(1, 1)], -5, 0),
        ([(1, 1), (0, 1)], -1, -1),
        ([(3, 10)], 0, -1),
        ([(0, 5), (0, 5), (-1, 0)], 0, 0),
        ([(5, 5), (0, 0), (0, -1)], 20, 1),
    ],
)
def test_violacao_lanca_value_error_e_preserva_a_lista(itens, desconto, frete):
    conteudo = list(itens)
    identidades = [id(item) for item in itens]
    with pytest.raises(ValueError):
        calcular_total(itens, desconto, frete)
    _assert_lista_intacta(itens, conteudo, identidades)


def test_preservacao_apos_erro_e_chamada_seguinte_independente():
    ruins = [(1, 80), (0, 20), (1, -5)]
    conteudo = list(ruins)
    identidades = [id(item) for item in ruins]
    with pytest.raises(ValueError):
        calcular_total(ruins, 10, 4)
    _assert_lista_intacta(ruins, conteudo, identidades)

    bons = [(1, 80), (0, 20)]
    assert _chama(bons, 10, 4) == 76
    with pytest.raises(ValueError):
        calcular_total(ruins, 0, 0)
    _assert_lista_intacta(ruins, conteudo, identidades)
    assert _chama(bons, 0, 0) == 80
    assert _chama([(1, 1)], 1, 0) == 0


def test_erro_na_primeira_linha_nao_altera_as_seguintes():
    itens = [(-1, 10), (2, 30), (0, 5)]
    conteudo = list(itens)
    identidades = [id(item) for item in itens]
    with pytest.raises(ValueError):
        calcular_total(itens, 0, 9)
    _assert_lista_intacta(itens, conteudo, identidades)


def test_validacao_depois_de_quantidade_zero_no_inicio_e_no_meio():
    for itens in (
        [(0, 1), (-1, 1)],
        [(0, 0), (0, 0), (1, -8)],
        [(2, 10), (0, 4), (-3, 1)],
        [(2, 10), (0, 4), (1, -1)],
        [(0, -1), (1, 1)],
        [(1, 1), (0, -2), (1, 1)],
    ):
        conteudo = list(itens)
        identidades = [id(item) for item in itens]
        with pytest.raises(ValueError):
            calcular_total(itens, 0, 1)
        _assert_lista_intacta(itens, conteudo, identidades)
