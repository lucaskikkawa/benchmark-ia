"""Testes do comportamento público de calcular_total (carrinho.py)."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from carrinho import calcular_total  # noqa: E402


# --- total bruto e carrinho vazio ---


def test_soma_quantidade_vezes_preco():
    assert calcular_total([(2, 150), (3, 100)]) == 600


def test_item_unico():
    assert calcular_total([(1, 999)]) == 999


def test_carrinho_vazio_total_zero():
    assert calcular_total([]) == 0


def test_carrinho_vazio_com_desconto_e_frete_total_zero():
    assert calcular_total([], desconto=50, frete=30) == 0


def test_argumentos_posicionais_e_nomeados_sao_equivalentes():
    assert calcular_total([(1, 100)], 10, 5) == calcular_total(
        [(1, 100)], desconto=10, frete=5
    )


# --- desconto ---


def test_desconto_padrao_zero_nao_altera_total():
    assert calcular_total([(2, 150)]) == 300
    assert calcular_total([(2, 150)], desconto=0) == 300


def test_desconto_100_zera_o_bruto():
    assert calcular_total([(5, 1000)], desconto=100) == 0


def test_desconto_percentual_simples():
    assert calcular_total([(1, 200)], desconto=25) == 150


def test_desconto_trunca_meio_centavo_para_baixo():
    # 15 * 50 / 100 = 7,5 -> 7 (nem arredondado para par, nem para cima)
    assert calcular_total([(1, 15)], desconto=50) == 7


def test_desconto_trunca_para_baixo_nao_sobe_para_cima():
    # 99 * 99 / 100 = 98,01 -> 98
    assert calcular_total([(1, 99)], desconto=1) == 98


def test_desconto_aplicado_uma_vez_sobre_o_bruto_agregado():
    # bruto = 30 -> 15 ; aplicar por linha daria 7 + 7 = 14
    assert calcular_total([(1, 15), (1, 15)], desconto=50) == 15


def test_truncamento_nao_e_feito_por_linha():
    # bruto = 2 -> 1 ; truncar cada linha daria 0 + 0 = 0
    assert calcular_total([(1, 1), (1, 1)], desconto=50) == 1


def test_truncamento_agregado_entre_varias_linhas():
    # bruto = 100 -> 90 ; por linha daria 89 + 0 = 89
    assert calcular_total([(3, 33), (1, 1)], desconto=10) == 90


# --- frete ---


def test_frete_somado_quando_ha_unidades():
    assert calcular_total([(1, 100)], frete=30) == 130


def test_frete_zero_aceito_e_nao_altera_total():
    assert calcular_total([(1, 100)], frete=0) == 100


def test_carrinho_vazio_nao_cobra_frete():
    assert calcular_total([], frete=30) == 0


def test_quantidade_zero_nao_cobra_frete():
    assert calcular_total([(0, 100)], frete=30) == 0


def test_so_linhas_de_quantidade_zero_nao_cobram_frete():
    assert calcular_total([(0, 100), (0, 5)], frete=30) == 0


def test_item_gratuito_com_quantidade_positiva_paga_frete():
    assert calcular_total([(1, 0)], frete=30) == 30


def test_frete_nao_recebe_desconto():
    assert calcular_total([(1, 100)], desconto=50, frete=30) == 80


def test_frete_entra_depois_do_truncamento_do_desconto():
    # 15 -> 7 com desconto de 50%; depois frete 3 -> 10
    # (aplicar desconto sobre bruto + frete daria 18 -> 9)
    assert calcular_total([(1, 15)], desconto=50, frete=3) == 10


def test_desconto_100_com_frete_cobra_so_o_frete():
    assert calcular_total([(5, 1000)], desconto=100, frete=5) == 5


# --- validação de desconto e frete ---


@pytest.mark.parametrize("desconto", [-1, -100, 101, 1000])
def test_desconto_fora_da_faixa_lanca_value_error(desconto):
    with pytest.raises(ValueError):
        calcular_total([(1, 100)], desconto=desconto)


@pytest.mark.parametrize("desconto", [-1, 101])
def test_desconto_invalido_com_carrinho_vazio_lanca_value_error(desconto):
    with pytest.raises(ValueError):
        calcular_total([], desconto=desconto)


def test_frete_negativo_lanca_value_error():
    with pytest.raises(ValueError):
        calcular_total([(1, 100)], frete=-1)


def test_frete_negativo_com_carrinho_vazio_lanca_value_error():
    with pytest.raises(ValueError):
        calcular_total([], frete=-1)


def test_frete_negativo_com_quantidade_zero_lanca_value_error():
    with pytest.raises(ValueError):
        calcular_total([(0, 100)], frete=-1)


# --- validação de linhas ---


def test_quantidade_negativa_lanca_value_error():
    with pytest.raises(ValueError):
        calcular_total([(-1, 100)])


def test_quantidade_negativa_em_segunda_linha_lanca_value_error():
    with pytest.raises(ValueError):
        calcular_total([(2, 100), (-1, 100)])


def test_preco_negativo_lanca_value_error():
    with pytest.raises(ValueError):
        calcular_total([(1, -1)])


def test_quantidade_zero_e_aceita():
    assert calcular_total([(0, 100)]) == 0


def test_preco_zero_e_aceito():
    assert calcular_total([(1, 0)]) == 0


def test_quantidade_zero_com_preco_negativo_lanca_value_error():
    with pytest.raises(ValueError):
        calcular_total([(0, -1)])


def test_linha_de_quantidade_zero_nao_encerra_o_processamento():
    assert calcular_total([(0, 500), (2, 10)]) == 20


def test_linha_de_quantidade_zero_ao_final_nao_altera_total():
    assert calcular_total([(2, 10), (0, 500)]) == 20


def test_linha_posterior_a_quantidade_zero_com_quantidade_negativa_lanca():
    with pytest.raises(ValueError):
        calcular_total([(0, 5), (-1, 10)])


def test_linha_posterior_a_quantidade_zero_com_preco_negativo_lanca():
    with pytest.raises(ValueError):
        calcular_total([(0, 5), (1, -1)])


def test_linha_posterior_a_quantidade_zero_com_preco_negativo_lanca_mesmo_com_zero():
    with pytest.raises(ValueError):
        calcular_total([(0, 5), (0, -1)])


def test_linha_posterior_a_quantidade_zero_valida_quando_correta():
    assert calcular_total([(0, 5), (1, 10)]) == 10


# --- inteiros de precisão arbitrária ---


def test_produto_acima_de_2_elevado_a_53_e_exato():
    assert calcular_total([(10**30, 10**20)]) == 10**50


def test_soma_acima_de_2_elevado_a_53_e_exata():
    assert calcular_total([(1, 2**53 + 1)]) == 2**53 + 1


def test_soma_de_linhas_grandes_e_exata():
    assert calcular_total([(1, 2**60 + 1), (1, 2**60 + 1)]) == 2**61 + 2


def test_desconto_sobre_valor_grande_e_exato():
    # (10**20 + 1) * 99 / 100 = 99000000000000000000,99 -> 99000000000000000000
    assert calcular_total([(1, 10**20 + 1)], desconto=1) == 99 * 10**18


def test_desconto_sobre_valor_acima_de_2_elevado_a_53_e_exato():
    # (2**53 + 1) * 99 / 100 -> 8917127262193583
    assert calcular_total([(1, 2**53 + 1)], desconto=1) == 8917127262193583


def test_frete_grande_e_exato():
    assert calcular_total([(1, 1)], frete=2**70) == 2**70 + 1


# --- lista de entrada intacta ---


def test_lista_nao_e_alterada_em_chamada_valida():
    itens = [(1, 10), (0, 5), (3, 7)]
    copia = list(itens)
    calcular_total(itens, desconto=10, frete=5)
    assert itens == copia


def test_lista_nao_e_alterada_quando_ha_value_error():
    itens = [(1, 10), (0, 5), (2, -1)]
    copia = list(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=10, frete=5)
    assert itens == copia


def test_lista_nao_e_alterada_quando_desconto_invalido():
    itens = [(1, 10), (2, 20)]
    copia = list(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=101)
    assert itens == copia


def test_lista_vazia_continua_vazia():
    itens = []
    calcular_total(itens, frete=10)
    assert itens == []


# --- chamadas independentes e preservação após erro ---


def test_mesma_chamada_repetida_retorna_o_mesmo_valor():
    itens = [(2, 150), (1, 15)]
    primeiro = calcular_total(itens, desconto=50, frete=3)
    segundo = calcular_total(itens, desconto=50, frete=3)
    # bruto = 315 -> 157 com desconto de 50%; mais frete 3 -> 160
    assert primeiro == segundo == 160


def test_chamada_com_frete_nao_vaza_para_a_seguinte():
    assert calcular_total([(1, 100)], frete=50) == 150
    assert calcular_total([(1, 100)]) == 100


def test_chamada_com_desconto_nao_vaza_para_a_seguinte():
    assert calcular_total([(1, 100)], desconto=50) == 50
    assert calcular_total([(1, 100)]) == 100


def test_chamada_com_unidades_nao_vaza_frete_para_carrinho_vazio():
    assert calcular_total([(1, 100)], frete=10) == 110
    assert calcular_total([], frete=10) == 0


def test_chamada_com_erro_nao_afeta_a_seguinte():
    with pytest.raises(ValueError):
        calcular_total([(1, 10), (2, -1)])
    assert calcular_total([(2, 50)]) == 100


def test_erro_de_desconto_nao_afeta_a_seguinte():
    with pytest.raises(ValueError):
        calcular_total([(1, 10)], desconto=200)
    assert calcular_total([(1, 10)], desconto=10) == 9


def test_erro_em_linha_posterior_nao_deixa_estado_residual():
    with pytest.raises(ValueError):
        calcular_total([(5, 100), (0, 1), (1, -1)], frete=7)
    assert calcular_total([(1, 100)]) == 100
    assert calcular_total([]) == 0
