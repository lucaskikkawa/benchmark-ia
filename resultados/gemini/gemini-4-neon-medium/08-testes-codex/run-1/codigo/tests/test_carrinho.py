import pytest

from carrinho import calcular_total


def test_carrinho_vazio_padrao_e_com_frete():
    resultado_padrao = calcular_total([])
    assert resultado_padrao == 0
    assert type(resultado_padrao) is int

    resultado_com_frete = calcular_total([], frete=1500)
    assert resultado_com_frete == 0
    assert type(resultado_com_frete) is int

    resultado_com_desconto_e_frete = calcular_total([], desconto=25, frete=1500)
    assert resultado_com_desconto_e_frete == 0
    assert type(resultado_com_desconto_e_frete) is int


def test_calculo_basico_e_argumentos_padrao_e_nomeados():
    assert calcular_total([(1, 1000)]) == 1000
    assert calcular_total([(3, 250)]) == 750
    assert calcular_total([(2, 100), (3, 250), (1, 50)]) == 1000
    assert calcular_total([(2, 100), (3, 100)]) == 500

    assert calcular_total([(2, 500)], 10, 300) == 1200
    assert calcular_total(itens=[(2, 500)], desconto=10, frete=300) == 1200
    assert calcular_total([(2, 500)], desconto=10) == 900
    assert calcular_total([(2, 500)], frete=300) == 1300


def test_bordas_desconto_zero_e_cem():
    res_zero = calcular_total([(2, 350)], desconto=0, frete=100)
    assert res_zero == 800
    assert type(res_zero) is int

    res_cem_sem_frete = calcular_total([(2, 350)], desconto=100, frete=0)
    assert res_cem_sem_frete == 0
    assert type(res_cem_sem_frete) is int

    res_cem_com_frete = calcular_total([(2, 350)], desconto=100, frete=250)
    assert res_cem_com_frete == 250
    assert type(res_cem_com_frete) is int

    assert calcular_total([(1, 100)], desconto=1) == 99
    assert calcular_total([(1, 100)], desconto=99) == 1
    assert calcular_total([(1, 99)], desconto=99) == 0


def test_truncamento_para_baixo_e_nao_arredondamento():
    # 101 * 99 / 100 = 99.99 -> deve truncar para 99 (nao 100 por round/ceil ou bruto - bruto*d//100)
    res1 = calcular_total([(1, 101)], desconto=1)
    assert res1 == 99
    assert type(res1) is int

    # 10 * 75 / 100 = 7.5 -> trunca para 7 (round daria 8)
    assert calcular_total([(1, 10)], desconto=25) == 7

    # 199 * 50 / 100 = 99.5 -> trunca para 99
    assert calcular_total([(1, 199)], desconto=50) == 99

    # 101 * 50 / 100 = 50.5 -> trunca para 50
    assert calcular_total([(1, 101)], desconto=50) == 50

    # 100 * (1 - 57 / 100) em float = 42.99999999999999 -> int() daria 42, exato eh 43
    assert calcular_total([(1, 100)], desconto=57) == 43
    assert calcular_total([(1, 100)], desconto=29) == 71


def test_truncamento_agregado_entre_linhas_e_unidades():
    # Por linha: (10*85//100) + (10*85//100) = 8 + 8 = 16; agregado: 20*85//100 = 17
    assert calcular_total([(1, 10), (1, 10)], desconto=15) == 17

    # Por linha: 1 + 1 + 2 = 4; agregado: 10*50//100 = 5
    assert calcular_total([(1, 3), (1, 3), (1, 4)], desconto=50) == 5

    # Por unidade: 3 * (3*50//100) = 3; agregado: 9*50//100 = 4
    assert calcular_total([(3, 3)], desconto=50) == 4

    # Muitas linhas pequenas cujo resto acumulado importa
    itens = [(1, 1)] * 10
    assert calcular_total(itens, desconto=10) == 9


def test_frete_sem_desconto_e_regras_de_quantidade_zero_e_item_gratuito():
    # Frete nao recebe desconto e eh cobrado uma unica vez
    assert calcular_total([(1, 1000)], desconto=50, frete=200) == 700
    assert calcular_total([(3, 100), (2, 200)], desconto=0, frete=500) == 1200

    # Item gratuito com quantidade positiva paga frete
    assert calcular_total([(1, 0)], frete=500) == 500
    assert calcular_total([(3, 0)], frete=500) == 500
    assert calcular_total([(0, 1000), (1, 0)], frete=500) == 500

    # Liquido truncado para zero com unidade positiva ainda paga frete
    assert calcular_total([(1, 1)], desconto=50, frete=500) == 500

    # Linhas com quantidade zero nao pagam frete
    assert calcular_total([(0, 1000)], frete=500) == 0
    assert calcular_total([(0, 0), (0, 500)], frete=500) == 0

    # Mistura de linha com quantidade zero e linha positiva
    assert calcular_total([(0, 999), (2, 100)], desconto=10, frete=300) == 480
    assert calcular_total([(2, 100), (0, 999)], desconto=10, frete=300) == 480
    assert calcular_total([(0, 100), (0, 200), (1, 50)], frete=25) == 75


@pytest.mark.parametrize(
    "itens,desconto,frete",
    [
        # Desconto fora da faixa (inclusive em carrinho vazio e quantidade zero)
        ([], -1, 0),
        ([], -100, 0),
        ([], 101, 0),
        ([], 200, 0),
        ([(0, 100)], -1, 0),
        ([(0, 100)], 101, 0),
        ([(1, 100)], -1, 0),
        ([(1, 100)], 101, 0),
        # Frete negativo (inclusive em carrinho vazio e quantidade zero)
        ([], 0, -1),
        ([], 0, -500),
        ([(0, 100)], 0, -1),
        ([(0, 0)], 0, -1),
        ([(1, 100)], 0, -1),
        # Quantidade negativa
        ([(-1, 100)], 0, 0),
        ([(-1, 0)], 0, 0),
        ([(2, 100), (-1, 50)], 0, 0),
        # Preco negativo (inclusive quando quantidade eh zero)
        ([(1, -1)], 0, 0),
        ([(0, -1)], 0, 0),
        ([(0, -100)], 0, 500),
        # Linhas invalidas posteriores a linha com quantidade zero
        ([(0, 100), (-1, 50)], 0, 0),
        ([(0, 100), (1, -50)], 0, 0),
        ([(0, 100), (0, -50)], 0, 0),
        ([(1, 100), (0, 50), (-1, 50)], 0, 0),
        ([(1, 100), (0, 50), (1, -50)], 0, 0),
    ],
)
def test_validacoes_lancam_value_error(itens, desconto, frete):
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=desconto, frete=frete)


def test_precisao_arbitraria_acima_de_2_elevado_a_53():
    grande = 2**53 + 100
    res_sem_desconto = calcular_total([(1, grande)], desconto=0, frete=0)
    assert res_sem_desconto == 2**53 + 100
    assert type(res_sem_desconto) is int

    res_com_desconto = calcular_total([(1, grande)], desconto=10, frete=7)
    assert res_com_desconto == (2**53 + 100) * 90 // 100 + 7
    assert type(res_com_desconto) is int

    muito_grande = 2**60 + 99
    res_muito_grande = calcular_total([(1, muito_grande)], desconto=33, frete=13)
    assert res_muito_grande == (2**60 + 99) * 67 // 100 + 13
    assert type(res_muito_grande) is int

    # Produto de quantidade grande por preco grande
    assert calcular_total([(10**18, 10**18)], desconto=0, frete=0) == 10**36
    assert calcular_total([(10**18, 10**18)], desconto=1, frete=2**60 + 3) == (
        10**36 * 99 // 100 + 2**60 + 3
    )

    # Soma de dois itens acima de 2**53 + truncamento
    a = 2**54 + 3
    b = 2**54 + 4
    assert calcular_total([(1, a), (1, b)], desconto=25, frete=1) == (a + b) * 75 // 100 + 1


def test_lista_nao_alterada_em_sucesso():
    itens = [(2, 300), (0, 100), (1, 50)]
    copia = list(itens)
    resultado = calcular_total(itens, desconto=10, frete=200)
    assert resultado == 785
    assert itens == copia


@pytest.mark.parametrize(
    "itens,desconto,frete",
    [
        ([(1, 100), (2, 200)], -1, 0),
        ([(1, 100), (2, 200)], 101, 0),
        ([(1, 100), (2, 200)], 0, -1),
        ([(1, 100), (-1, 200), (3, 300)], 0, 0),
        ([(0, 100), (1, -50), (2, 300)], 0, 0),
        ([(0, -1), (2, 300)], 10, 50),
    ],
)
def test_lista_preservada_apos_erro(itens, desconto, frete):
    copia = list(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=desconto, frete=frete)
    assert itens == copia


def test_chamadas_independentes_e_sem_estado_compartilhado():
    assert calcular_total([(2, 500)], desconto=10, frete=100) == 1000
    assert calcular_total([(1, 200)]) == 200
    assert calcular_total([], frete=500) == 0

    with pytest.raises(ValueError):
        calcular_total([(1, -10)], desconto=50, frete=300)

    assert calcular_total([(2, 100)], desconto=0, frete=0) == 200

    # Mesma instancia de lista modificada externamente entre chamadas
    itens = [(1, 100)]
    assert calcular_total(itens) == 100
    itens.append((2, 200))
    assert calcular_total(itens) == 500
