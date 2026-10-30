import copy
import os
import sys

import pytest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from carrinho import calcular_total  # noqa: E402


# --- Caso básico e sem desconto/frete -------------------------------------

def test_soma_simples_sem_desconto_nem_frete():
    assert calcular_total([(2, 100), (3, 50)]) == 350


def test_argumentos_padrao_sao_zero():
    assert calcular_total([(1, 100)]) == 100
    assert calcular_total([(1, 100)], desconto=0, frete=0) == 100


def test_argumentos_nomeados():
    assert calcular_total([(1, 100)], frete=5, desconto=10) == 95


def test_preco_zero_com_quantidade_positiva_retorna_zero():
    assert calcular_total([(5, 0)]) == 0


# --- Desconto -------------------------------------------------------------

def test_desconto_aplicado_uma_vez_sobre_bruto_com_truncamento_agregado():
    # bruto 30; 30 * 90 // 100 = 27. Truncar por linha daria 13 + 13 = 26.
    assert calcular_total([(1, 15), (1, 15)], desconto=10) == 27


def test_truncamento_para_baixo_em_caso_unico():
    # 99 * 90 = 8910; 8910 // 100 = 89 (não arredonda para 89.1 -> 90)
    assert calcular_total([(1, 99)], desconto=10) == 89


def test_truncamento_agregado_entre_varias_linhas():
    # bruto = 3*7 + 5*11 + 2*13 = 21 + 55 + 26 = 102
    # 102 * 75 // 100 = 76 (7650 / 100 = 76.5)
    itens = [(3, 7), (5, 11), (2, 13)]
    assert calcular_total(itens, desconto=25) == 76


def test_desconto_zero_nao_altera_valor():
    assert calcular_total([(4, 25)], desconto=0) == 100


def test_desconto_100_zera_bruto():
    assert calcular_total([(2, 50)], desconto=100) == 0


def test_desconto_100_com_frete_cobra_somente_frete():
    assert calcular_total([(2, 50)], desconto=100, frete=7) == 7


def test_desconto_em_bruto_zero_resulta_zero():
    assert calcular_total([(0, 500)], desconto=50) == 0


@pytest.mark.parametrize("desconto", [-1, 101, 150, -100])
def test_desconto_fora_do_intervalo_levanta_valueerror(desconto):
    with pytest.raises(ValueError):
        calcular_total([(1, 100)], desconto=desconto)


# --- Frete ----------------------------------------------------------------

def test_frete_nao_recebe_desconto():
    # 50 com desconto de 50% + frete 30 integral = 80
    assert calcular_total([(1, 100)], desconto=50, frete=30) == 80


def test_frete_somado_depois_do_desconto_sem_truncar_a_mais():
    # 33 * 90 // 100 = 29; + 1 = 30
    assert calcular_total([(1, 33)], desconto=10, frete=1) == 30


def test_item_gratuito_com_quantidade_positiva_paga_frete():
    assert calcular_total([(1, 0)], frete=25) == 25


def test_linha_com_quantidade_zero_nao_gera_frete():
    assert calcular_total([(0, 100)], frete=25) == 0


def test_quantidade_zero_junto_com_linha_positiva_paga_frete_uma_vez():
    assert calcular_total([(0, 100), (2, 10)], frete=25) == 45


def test_frete_zero_nao_altera_valor():
    assert calcular_total([(2, 10)], frete=0) == 20


def test_frete_negativo_levanta_valueerror():
    with pytest.raises(ValueError):
        calcular_total([(1, 100)], frete=-1)


def test_frete_com_soma_zero_de_quantidades_nao_e_cobrado():
    assert calcular_total([(0, 10), (0, 20)], desconto=10, frete=99) == 0


# --- Validação de entradas ------------------------------------------------

def test_quantidade_negativa_levanta_valueerror():
    with pytest.raises(ValueError):
        calcular_total([(-1, 100)])


def test_preco_negativo_levanta_valueerror():
    with pytest.raises(ValueError):
        calcular_total([(1, -100)])


def test_preco_negativo_em_linha_de_quantidade_zero_levanta_valueerror():
    with pytest.raises(ValueError):
        calcular_total([(0, -5)])


def test_linha_invalida_apos_linha_de_quantidade_zero_levanta_valueerror():
    with pytest.raises(ValueError):
        calcular_total([(0, 10), (1, -1)])


def test_quantidade_negativa_apos_linha_de_quantidade_zero_levanta_valueerror():
    with pytest.raises(ValueError):
        calcular_total([(0, 10), (-1, 5)])


def test_quantidade_negativa_no_fim_com_varias_linhas_levanta_valueerror():
    with pytest.raises(ValueError):
        calcular_total([(1, 10), (2, 20), (3, 30), (-4, 40)])


def test_valores_validos_nos_limites_nao_levantam():
    assert calcular_total([(0, 0)]) == 0
    assert calcular_total([(1, 0)], desconto=100, frete=0) == 0


# --- Precisão arbitrária --------------------------------------------------

def test_resultado_exato_acima_de_2_a_53():
    preco = 2**60 + 1
    assert calcular_total([(1, preco)]) == 2**60 + 1


def test_total_grande_com_desconto_exato():
    # bruto = (2**53 + 1) * 3 ; desconto 1 -> bruto * 99 // 100
    bruto = (2**53 + 1) * 3
    esperado = bruto * 99 // 100
    assert calcular_total([(3, 2**53 + 1)], desconto=1) == esperado


def test_quantidade_muito_grande_exata():
    q = 10**30
    p = 10**20
    assert calcular_total([(q, p)]) == 10**50


def test_desconto_com_inteiros_grandes_nao_perde_precisao():
    v = 2**80 + 7
    assert calcular_total([(1, v)], desconto=33) == v * 67 // 100


# --- Não alterar a lista e independência de chamadas ----------------------

def test_lista_nao_e_alterada_em_caso_valido():
    itens = [(2, 100), (0, 50), (1, 7)]
    original = copy.deepcopy(itens)
    calcular_total(itens, desconto=10, frete=5)
    assert itens == original


def test_lista_nao_e_alterada_quando_lanca_valueerror():
    itens = [(1, 100), (0, 10), (-1, 5)]
    original = copy.deepcopy(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=10, frete=5)
    assert itens == original


def test_lista_nao_e_alterada_quando_desconto_invalido():
    itens = [(1, 100), (2, 3)]
    original = copy.deepcopy(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=101)
    assert itens == original


def test_chamadas_sao_independentes():
    assert calcular_total([(1, 100)], desconto=50, frete=10) == 60
    assert calcular_total([(2, 5)]) == 10
    assert calcular_total([(1, 100)], desconto=50, frete=10) == 60


def test_erro_nao_afeta_chamada_seguinte():
    with pytest.raises(ValueError):
        calcular_total([(1, -1)], frete=3)
    assert calcular_total([(1, 100)], frete=3) == 103


def test_erro_de_desconto_nao_afeta_chamada_seguinte():
    with pytest.raises(ValueError):
        calcular_total([(1, 100)], desconto=200)
    assert calcular_total([(1, 100)], desconto=10) == 90


def test_mesma_lista_reutilizada_da_mesma_resposta():
    itens = [(3, 33), (1, 1)]
    primeiro = calcular_total(itens, desconto=20, frete=4)
    segundo = calcular_total(itens, desconto=20, frete=4)
    # bruto = 3*33 + 1*1 = 100; 100 * 80 // 100 = 80; + frete 4
    assert primeiro == segundo == 84
