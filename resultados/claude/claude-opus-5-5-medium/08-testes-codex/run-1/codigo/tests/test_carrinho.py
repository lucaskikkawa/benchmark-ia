import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from carrinho import calcular_total  # noqa: E402


# ---------- cálculo básico ----------

def test_carrinho_vazio_sem_frete():
    assert calcular_total([]) == 0
    assert calcular_total([], 0, 0) == 0
    assert calcular_total([], frete=500) == 0
    assert calcular_total([], desconto=100, frete=500) == 0
    assert calcular_total([], desconto=50, frete=1) == 0


def test_item_unico():
    assert calcular_total([(1, 1000)]) == 1000
    assert calcular_total([(3, 250)]) == 750


def test_soma_varias_linhas():
    assert calcular_total([(2, 300), (1, 450), (4, 25)]) == 600 + 450 + 100


def test_quantidade_vezes_preco_nao_soma():
    assert calcular_total([(3, 7)]) == 21
    assert calcular_total([(7, 3), (2, 5)]) == 31


def test_padroes_desconto_e_frete_zero():
    assert calcular_total([(2, 999)]) == 1998
    assert calcular_total([(2, 999)], 0) == 1998


# ---------- desconto ----------

def test_desconto_simples():
    assert calcular_total([(1, 1000)], desconto=10) == 900
    assert calcular_total([(4, 250)], desconto=25) == 750


def test_desconto_zero_e_cem():
    assert calcular_total([(1, 1234)], desconto=0) == 1234
    assert calcular_total([(1, 1234)], desconto=100) == 0
    assert calcular_total([(1, 1234)], desconto=100, frete=300) == 300


def test_desconto_99_e_1():
    assert calcular_total([(1, 1000)], desconto=99) == 10
    assert calcular_total([(1, 1000)], desconto=1) == 990
    assert calcular_total([(1, 199)], desconto=99) == 1  # 199*1//100
    assert calcular_total([(1, 199)], desconto=1) == 197  # 199*99//100 = 197.01


def test_truncamento_para_baixo():
    # 999 * 90 / 100 = 899.1 -> 899
    assert calcular_total([(1, 999)], desconto=10) == 899
    # 1 * 50 / 100 = 0.5 -> 0 (não arredonda para 1)
    assert calcular_total([(1, 1)], desconto=50) == 0
    # 3 * 33 / 100 = 0.99 -> 0
    assert calcular_total([(1, 3)], desconto=67) == 0
    # 199 * 50 / 100 = 99.5 -> 99
    assert calcular_total([(1, 199)], desconto=50) == 99
    # 7 * 85 / 100 = 5.95 -> 5
    assert calcular_total([(1, 7)], desconto=15) == 5


def test_truncamento_agregado_entre_linhas():
    # por linha: 1*50//100 = 0 cada -> 0; agregado: 3*50//100 = 1
    assert calcular_total([(1, 1), (1, 1), (1, 1)], desconto=50) == 1
    # por linha: 5*90//100=4 duas vezes =8; agregado: 10*90//100 = 9
    assert calcular_total([(1, 5), (1, 5)], desconto=10) == 9
    # por unidade vs por linha: 3 unidades de 5 com 10%: 15*90//100 = 13
    assert calcular_total([(3, 5)], desconto=10) == 13
    # várias linhas com centavos fracionários
    itens = [(1, 33), (1, 33), (1, 34)]
    assert calcular_total(itens, desconto=33) == 67


def test_desconto_aplicado_uma_vez():
    assert calcular_total([(1, 10000)], desconto=50) == 5000
    assert calcular_total([(1, 10000)], desconto=20) == 8000
    assert calcular_total([(2, 5000), (1, 10000)], desconto=50) == 10000


def test_desconto_nao_incide_no_frete():
    assert calcular_total([(1, 1000)], desconto=50, frete=1000) == 1500
    assert calcular_total([(1, 999)], desconto=10, frete=101) == 899 + 101
    assert calcular_total([(1, 1)], desconto=50, frete=1) == 1


def test_truncamento_antes_do_frete():
    # (199*50//100)=99 + 1 = 100 ; se truncar depois do frete: (99.5+1) -> 100 também
    # usar caso que difere: 1*50//100 = 0, + 3 = 3
    assert calcular_total([(1, 1)], desconto=50, frete=3) == 3
    assert calcular_total([(1, 3)], desconto=50, frete=7) == 1 + 7


# ---------- frete ----------

def test_frete_com_unidades():
    assert calcular_total([(1, 1000)], frete=500) == 1500
    assert calcular_total([(2, 100), (3, 10)], frete=1) == 231


def test_frete_zero():
    assert calcular_total([(1, 1000)], frete=0) == 1000


def test_frete_item_gratuito_com_quantidade_positiva():
    assert calcular_total([(1, 0)], frete=500) == 500
    assert calcular_total([(5, 0)], desconto=30, frete=700) == 700


def test_sem_frete_quando_todas_quantidades_zero():
    assert calcular_total([(0, 1000)], frete=500) == 0
    assert calcular_total([(0, 1000), (0, 5)], frete=500) == 0
    assert calcular_total([(0, 0)], frete=500) == 0
    assert calcular_total([(0, 1000)], desconto=10, frete=500) == 0


def test_frete_com_mistura_de_linhas_zero_e_positivas():
    assert calcular_total([(0, 1000), (1, 0)], frete=500) == 500
    assert calcular_total([(0, 1000), (1, 10)], frete=500) == 510
    assert calcular_total([(1, 10), (0, 1000)], frete=500) == 510


def test_frete_cobrado_uma_vez():
    assert calcular_total([(1, 10), (1, 10), (1, 10)], frete=100) == 130
    assert calcular_total([(5, 10)], frete=100) == 150


# ---------- validação ----------

@pytest.mark.parametrize("desconto", [-1, 101, -100, 200, 10**30, -(10**30)])
def test_desconto_invalido(desconto):
    with pytest.raises(ValueError):
        calcular_total([(1, 100)], desconto=desconto)


@pytest.mark.parametrize("desconto", [-1, 101])
def test_desconto_invalido_carrinho_vazio(desconto):
    with pytest.raises(ValueError):
        calcular_total([], desconto=desconto)


@pytest.mark.parametrize("desconto", [-1, 101])
def test_desconto_invalido_quantidade_zero(desconto):
    with pytest.raises(ValueError):
        calcular_total([(0, 100)], desconto=desconto)


@pytest.mark.parametrize("frete", [-1, -500, -(10**30)])
def test_frete_negativo(frete):
    with pytest.raises(ValueError):
        calcular_total([(1, 100)], frete=frete)
    with pytest.raises(ValueError):
        calcular_total([], frete=frete)
    with pytest.raises(ValueError):
        calcular_total([(0, 100)], frete=frete)


def test_quantidade_negativa():
    with pytest.raises(ValueError):
        calcular_total([(-1, 100)])
    with pytest.raises(ValueError):
        calcular_total([(-1, 0)])
    with pytest.raises(ValueError):
        calcular_total([(-1, 100)], desconto=100)


def test_preco_negativo():
    with pytest.raises(ValueError):
        calcular_total([(1, -1)])
    with pytest.raises(ValueError):
        calcular_total([(0, -1)])
    with pytest.raises(ValueError):
        calcular_total([(1, -1)], desconto=100)


def test_negativos_que_se_cancelariam():
    with pytest.raises(ValueError):
        calcular_total([(-1, -100)])
    with pytest.raises(ValueError):
        calcular_total([(2, 100), (-1, 100)])
    with pytest.raises(ValueError):
        calcular_total([(2, 100), (1, -100)])


def test_linha_invalida_apos_linha_valida():
    with pytest.raises(ValueError):
        calcular_total([(1, 100), (1, 100), (-1, 50)])
    with pytest.raises(ValueError):
        calcular_total([(1, 100), (1, 100), (1, -50)])


def test_validacao_apos_linha_quantidade_zero():
    with pytest.raises(ValueError):
        calcular_total([(0, 100), (-1, 100)])
    with pytest.raises(ValueError):
        calcular_total([(0, 100), (1, -100)])
    with pytest.raises(ValueError):
        calcular_total([(0, 100), (0, -1)])
    with pytest.raises(ValueError):
        calcular_total([(1, 100), (0, 5), (-2, 100)])
    with pytest.raises(ValueError):
        calcular_total([(0, 0), (0, 0), (3, -1)])


def test_quantidade_zero_preco_negativo():
    with pytest.raises(ValueError):
        calcular_total([(0, -5)], frete=0)


def test_limites_validos_zero():
    assert calcular_total([(0, 0)]) == 0
    assert calcular_total([(1, 0)]) == 0
    assert calcular_total([(0, 1)]) == 0
    assert calcular_total([(1, 1)], desconto=0, frete=0) == 1


# ---------- inteiros grandes ----------

def test_inteiros_grandes_exatos():
    preco = 2**53 + 1
    assert calcular_total([(1, preco)]) == preco
    assert calcular_total([(3, preco)]) == 3 * preco
    grande = 10**30 + 7
    assert calcular_total([(1, grande)], desconto=10) == grande * 90 // 100
    assert calcular_total([(3, grande), (2, 1)], desconto=33, frete=2**60 + 1) == (
        (3 * grande + 2) * 67 // 100 + 2**60 + 1
    )


def test_inteiros_grandes_desconto_truncado_exato():
    bruto = 2**64 + 99
    assert calcular_total([(1, bruto)], desconto=1) == bruto * 99 // 100
    assert calcular_total([(1, bruto)], desconto=50) == bruto // 2
    q = 10**20 + 3
    p = 10**20 + 9
    assert calcular_total([(q, p)], desconto=7, frete=1) == q * p * 93 // 100 + 1


def test_frete_grande():
    f = 2**70 + 3
    assert calcular_total([(1, 1)], frete=f) == 1 + f
    assert calcular_total([(0, 1)], frete=f) == 0


def test_quantidade_grande():
    q = 2**60 + 1
    assert calcular_total([(q, 0)], frete=5) == 5
    assert calcular_total([(q, 3)]) == 3 * q


# ---------- imutabilidade e independência ----------

def test_lista_nao_alterada():
    itens = [(2, 300), (0, 100), (1, 450)]
    copia = list(itens)
    elementos = [id(x) for x in itens]
    calcular_total(itens, desconto=10, frete=50)
    assert itens == copia
    assert [id(x) for x in itens] == elementos
    assert len(itens) == 3


def test_lista_vazia_nao_alterada():
    itens = []
    calcular_total(itens, frete=10)
    assert itens == []


@pytest.mark.parametrize(
    "itens, kwargs",
    [
        ([(1, 100), (-1, 100), (2, 5)], {}),
        ([(1, 100), (1, -100), (2, 5)], {}),
        ([(0, 100), (-1, 100)], {}),
        ([(1, 100), (2, 3)], {"desconto": 101}),
        ([(1, 100), (2, 3)], {"desconto": -1}),
        ([(1, 100), (2, 3)], {"frete": -1}),
    ],
)
def test_lista_intacta_apos_erro(itens, kwargs):
    copia = list(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, **kwargs)
    assert itens == copia


def test_preservacao_apos_erro():
    itens = [(1, 100), (-1, 50), (3, 7)]
    copia = list(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=10, frete=5)
    assert itens == copia
    # chamada válida após erro funciona normalmente
    assert calcular_total([(1, 100)], frete=5) == 105
    assert calcular_total([(2, 50)], desconto=10, frete=5) == 95
    assert calcular_total([]) == 0
    with pytest.raises(ValueError):
        calcular_total(itens)
    assert itens == copia


def test_chamadas_independentes():
    a = [(1, 100)]
    b = [(2, 300)]
    assert calcular_total(a) == 100
    assert calcular_total(b) == 600
    assert calcular_total(a) == 100
    assert calcular_total(a, desconto=50) == 50
    assert calcular_total(a) == 100
    assert calcular_total(a, frete=10) == 110
    assert calcular_total(a) == 100
    assert calcular_total([(0, 1)], frete=10) == 0
    assert calcular_total([(1, 0)], frete=10) == 10
    assert calcular_total([(0, 1)], frete=10) == 0
    assert calcular_total([]) == 0


def test_mesma_lista_repetida():
    itens = [(1, 999), (2, 1)]
    copia = list(itens)
    r1 = calcular_total(itens, desconto=10, frete=3)
    r2 = calcular_total(itens, desconto=10, frete=3)
    assert r1 == r2 == 1001 * 90 // 100 + 3
    assert itens == copia


def test_retorna_int():
    r = calcular_total([(1, 999)], desconto=10, frete=1)
    assert type(r) is int
    assert type(calcular_total([])) is int
    assert type(calcular_total([(1, 1)], desconto=50)) is int

