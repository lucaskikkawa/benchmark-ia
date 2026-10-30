import copy

import pytest

from carrinho import calcular_total


# ---------- cálculo básico ----------

def test_carrinho_vazio_sem_frete():
    assert calcular_total([]) == 0
    assert calcular_total([], desconto=50, frete=999) == 0


def test_um_item():
    assert calcular_total([(1, 1000)]) == 1000


def test_soma_quantidade_vezes_preco():
    assert calcular_total([(2, 150), (3, 7), (1, 1)]) == 300 + 21 + 1


def test_defaults_desconto_e_frete_zero():
    assert calcular_total([(4, 25)]) == 100


# ---------- desconto ----------

@pytest.mark.parametrize(
    "itens, desconto, esperado",
    [
        ([(1, 1000)], 0, 1000),
        ([(1, 1000)], 10, 900),
        ([(1, 1000)], 100, 0),
        ([(1, 1000)], 1, 990),
        ([(1, 1000)], 99, 10),
        ([(1, 999)], 50, 499),     # 499.5 -> 499
        ([(1, 1)], 50, 0),         # 0.5 -> 0
        ([(1, 199)], 1, 197),      # 197.01 -> 197
        ([(1, 199)], 99, 1),       # 1.99 -> 1 (não arredonda para cima)
        ([(3, 33)], 33, 66),       # 99*67/100 = 66.33
    ],
)
def test_desconto_trunca_para_baixo(itens, desconto, esperado):
    assert calcular_total(itens, desconto=desconto) == esperado


def test_desconto_aplicado_uma_vez_sobre_bruto_agregado():
    # por linha: 1*1 -> 0 (truncado) duas vezes = 0; agregado: 2*50//100 = 1
    assert calcular_total([(1, 1), (1, 1)], desconto=50) == 1
    # 3 linhas de 1 centavo com 50%: 3*50//100 = 1
    assert calcular_total([(1, 1), (1, 1), (1, 1)], desconto=50) == 1
    # linhas de 5 com 30%: por linha 3 -> 6; agregado 10*70//100 = 7
    assert calcular_total([(1, 5), (1, 5)], desconto=30) == 7


def test_desconto_por_unidade_nao_e_truncado_separadamente():
    # por unidade: 1*50//100=0 ... ; bruto 3*1=3 -> 3*50//100=1
    assert calcular_total([(3, 1)], desconto=50) == 1
    assert calcular_total([(7, 3)], desconto=50) == 10  # 21*50//100=10


def test_desconto_nao_aplicado_duas_vezes():
    assert calcular_total([(1, 10000)], desconto=10) == 9000
    assert calcular_total([(1, 10000)], desconto=50) == 5000


def test_desconto_nao_incide_sobre_frete():
    assert calcular_total([(1, 1000)], desconto=10, frete=500) == 900 + 500
    assert calcular_total([(1, 1000)], desconto=100, frete=500) == 500
    assert calcular_total([(1, 1)], desconto=50, frete=1) == 1


# ---------- frete ----------

def test_frete_somado_com_unidades():
    assert calcular_total([(1, 1000)], frete=250) == 1250


def test_frete_zero_permitido():
    assert calcular_total([(2, 10)], frete=0) == 20


def test_item_gratuito_com_quantidade_positiva_paga_frete():
    assert calcular_total([(1, 0)], frete=300) == 300
    assert calcular_total([(5, 0)], desconto=100, frete=7) == 7


def test_linhas_quantidade_zero_nao_pagam_frete():
    assert calcular_total([(0, 1000)], frete=300) == 0
    assert calcular_total([(0, 1000), (0, 5)], desconto=10, frete=300) == 0


def test_frete_com_mistura_de_quantidade_zero_e_positiva():
    assert calcular_total([(0, 1000), (1, 0)], frete=300) == 300
    assert calcular_total([(0, 1000), (2, 5)], frete=300) == 310


def test_desconto_total_com_unidades_ainda_paga_frete():
    assert calcular_total([(2, 500)], desconto=100, frete=40) == 40


def test_frete_adicionado_uma_vez():
    assert calcular_total([(1, 10), (1, 10), (1, 10)], frete=5) == 35


# ---------- inteiros grandes ----------

def test_resultado_exato_acima_de_2_53():
    preco = 2**53 + 1
    assert calcular_total([(1, preco)]) == 2**53 + 1
    assert calcular_total([(3, preco)], frete=1) == 3 * (2**53 + 1) + 1


def test_desconto_exato_com_inteiros_grandes():
    preco = 10**20 + 1
    assert calcular_total([(1, preco)], desconto=1) == (preco * 99) // 100
    assert calcular_total([(1, preco)], desconto=1) == 99000000000000000000
    grande = 2**60 + 3
    assert calcular_total([(7, grande)], desconto=33, frete=2**55 + 1) == (
        7 * grande * 67 // 100 + 2**55 + 1
    )


def test_frete_grande_exato():
    assert calcular_total([(1, 1)], frete=2**64 + 1) == 2**64 + 2


# ---------- validação ----------

@pytest.mark.parametrize("desconto", [-1, 101, -100, 1000])
def test_desconto_fora_da_faixa(desconto):
    with pytest.raises(ValueError):
        calcular_total([(1, 100)], desconto=desconto)


@pytest.mark.parametrize("desconto", [-1, 101])
def test_desconto_invalido_em_carrinho_vazio(desconto):
    with pytest.raises(ValueError):
        calcular_total([], desconto=desconto)


@pytest.mark.parametrize("desconto", [0, 100])
def test_bordas_validas_de_desconto(desconto):
    calcular_total([(1, 100)], desconto=desconto)
    calcular_total([], desconto=desconto)


def test_frete_negativo():
    with pytest.raises(ValueError):
        calcular_total([(1, 100)], frete=-1)


def test_frete_negativo_em_carrinho_vazio():
    with pytest.raises(ValueError):
        calcular_total([], frete=-1)


def test_frete_negativo_com_quantidade_zero():
    with pytest.raises(ValueError):
        calcular_total([(0, 100)], frete=-1)


def test_quantidade_negativa():
    with pytest.raises(ValueError):
        calcular_total([(-1, 100)])


def test_quantidade_negativa_com_preco_zero():
    with pytest.raises(ValueError):
        calcular_total([(-1, 0)])


def test_preco_negativo():
    with pytest.raises(ValueError):
        calcular_total([(1, -1)])


def test_preco_negativo_com_quantidade_zero():
    with pytest.raises(ValueError):
        calcular_total([(0, -1)])


def test_quantidades_negativas_que_somariam_zero_ou_positivo():
    with pytest.raises(ValueError):
        calcular_total([(2, 10), (-1, 10)])
    with pytest.raises(ValueError):
        calcular_total([(1, 10), (-1, 10)], frete=5)


def test_precos_negativos_que_compensariam():
    with pytest.raises(ValueError):
        calcular_total([(1, 10), (1, -5)])


def test_validacao_de_linhas_apos_quantidade_zero():
    with pytest.raises(ValueError):
        calcular_total([(0, 100), (1, -1)])
    with pytest.raises(ValueError):
        calcular_total([(0, 100), (-1, 100)])
    with pytest.raises(ValueError):
        calcular_total([(0, 100), (0, -5)])
    with pytest.raises(ValueError):
        calcular_total([(1, 100), (0, 100), (2, -3)])


def test_linha_invalida_no_final():
    with pytest.raises(ValueError):
        calcular_total([(1, 1), (1, 1), (1, 1), (-1, 1)])
    with pytest.raises(ValueError):
        calcular_total([(1, 1), (1, 1), (1, 1), (1, -1)])


def test_quantidade_e_preco_zero_validos():
    assert calcular_total([(0, 0)]) == 0
    assert calcular_total([(0, 0)], frete=10) == 0
    assert calcular_total([(0, 5), (3, 0)], frete=10) == 10


# ---------- imutabilidade da entrada ----------

def test_lista_nao_alterada():
    itens = [(3, 100), (0, 50), (1, 0), (2, 7)]
    original = copy.deepcopy(itens)
    calcular_total(itens, desconto=10, frete=5)
    assert itens == original
    assert len(itens) == 4


def test_lista_nao_alterada_vazia():
    itens = []
    calcular_total(itens, frete=10)
    assert itens == []


@pytest.mark.parametrize(
    "itens, kwargs",
    [
        ([(1, 100), (2, 200), (-1, 5)], {}),
        ([(1, 100), (0, 5), (2, -1)], {}),
        ([(1, 100), (2, 200)], {"desconto": 101}),
        ([(1, 100), (2, 200)], {"desconto": -1}),
        ([(1, 100), (2, 200)], {"frete": -1}),
        ([(5, 1), (-1, 1), (3, 3)], {"desconto": 10, "frete": 2}),
    ],
)
def test_lista_nao_alterada_apos_erro(itens, kwargs):
    original = copy.deepcopy(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, **kwargs)
    assert itens == original
    assert [tuple(linha) for linha in itens] == original


def test_preservacao_apos_erro_e_uso_posterior():
    itens = [(2, 100), (1, 50)]
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=101)
    assert itens == [(2, 100), (1, 50)]
    assert calcular_total(itens, desconto=10, frete=3) == 225 + 3
    assert itens == [(2, 100), (1, 50)]


def test_erro_nao_contamina_chamadas_seguintes():
    with pytest.raises(ValueError):
        calcular_total([(5, 100), (-1, 1)])
    assert calcular_total([(1, 10)]) == 10
    with pytest.raises(ValueError):
        calcular_total([(5, 100), (1, -1)], frete=7)
    assert calcular_total([(0, 10)], frete=7) == 0
    assert calcular_total([(1, 10)], frete=7) == 17


# ---------- independência entre chamadas ----------

def test_chamadas_independentes():
    assert calcular_total([(1, 100)], frete=10) == 110
    assert calcular_total([(1, 100)], frete=10) == 110
    assert calcular_total([]) == 0
    assert calcular_total([(0, 100)], frete=10) == 0
    assert calcular_total([(2, 50)], desconto=50) == 50
    assert calcular_total([(2, 50)]) == 100


def test_chamadas_independentes_ordem_inversa():
    assert calcular_total([(0, 100)], frete=10) == 0
    assert calcular_total([(1, 0)], frete=10) == 10
    assert calcular_total([(0, 100)], frete=10) == 0
    assert calcular_total([(1, 1)], desconto=50) == 0
    assert calcular_total([(1, 1)], desconto=50) == 0


def test_mesma_lista_reutilizada():
    itens = [(1, 1), (1, 1)]
    for _ in range(3):
        assert calcular_total(itens, desconto=50, frete=1) == 2
    assert itens == [(1, 1), (1, 1)]


def test_ordem_das_linhas_nao_importa():
    a = [(1, 3), (0, 7), (2, 5)]
    b = list(reversed(a))
    assert calcular_total(a, desconto=33, frete=4) == calcular_total(b, desconto=33, frete=4)
    assert calcular_total(a, desconto=33, frete=4) == 13 * 67 // 100 + 4
