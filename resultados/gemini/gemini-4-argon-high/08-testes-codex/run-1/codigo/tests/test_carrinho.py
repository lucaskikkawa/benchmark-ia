import pytest
from carrinho import calcular_total


def test_carrinho_vazio_e_defaults():
    itens = []
    assert calcular_total(itens) == 0
    assert itens == []
    assert calcular_total([], desconto=0, frete=0) == 0
    assert calcular_total([], desconto=50, frete=100) == 0
    assert calcular_total([], desconto=100, frete=100) == 0


def test_calculo_basico_e_argumentos_padrao():
    itens = [(1, 100)]
    assert calcular_total(itens) == 100
    assert itens == [(1, 100)]
    assert calcular_total([(2, 150), (3, 50)]) == 450
    assert calcular_total([(2, 150)], 10) == 270
    assert calcular_total([(2, 150)], 10, 30) == 300
    assert calcular_total(itens=[(2, 150)], desconto=10, frete=30) == 300


def test_bordas_desconto_e_frete():
    assert calcular_total([(1, 200)], desconto=0, frete=0) == 200
    assert calcular_total([(1, 200)], desconto=100, frete=0) == 0
    assert calcular_total([(1, 200)], desconto=100, frete=50) == 50
    assert calcular_total([(1, 200)], desconto=0, frete=50) == 250


def test_truncamento_para_baixo_e_agregado_entre_linhas():
    # Truncamento para baixo do líquido: bruto * (100 - desconto) // 100
    assert calcular_total([(1, 10)], desconto=5) == 9
    assert calcular_total([(1, 9)], desconto=1) == 8
    assert calcular_total([(1, 99)], desconto=1) == 98
    assert calcular_total([(1, 1)], desconto=5) == 0

    # Desconto aplicado uma única vez sobre o bruto agregado (não por linha nem por unidade)
    assert calcular_total([(1, 10), (1, 10)], desconto=5) == 19
    assert calcular_total([(1, 1), (1, 1)], desconto=50) == 1
    assert calcular_total([(2, 1)], desconto=50) == 1
    assert calcular_total([(1, 3), (1, 3), (1, 3)], desconto=50) == 4
    assert calcular_total([(2, 3), (3, 3)], desconto=50) == 7


def test_regras_de_frete_e_quantidade_zero_ou_item_gratuito():
    # Frete não sofre desconto
    assert calcular_total([(1, 100)], desconto=50, frete=20) == 70

    # Item gratuito com quantidade positiva paga frete
    assert calcular_total([(1, 0)], desconto=0, frete=25) == 25
    assert calcular_total([(3, 0)], desconto=50, frete=40) == 40
    assert calcular_total([(1, 1)], desconto=50, frete=25) == 25

    # Linhas com quantidade zero não pagam frete
    assert calcular_total([(0, 100)], desconto=0, frete=25) == 0
    assert calcular_total([(0, 100), (0, 200)], desconto=10, frete=25) == 0
    assert calcular_total([(0, 0)], desconto=0, frete=25) == 0

    # Linha válida após linha com quantidade zero
    assert calcular_total([(0, 100), (2, 50)], desconto=10, frete=15) == 105
    assert calcular_total([(0, 100), (1, 0)], desconto=0, frete=15) == 15


def test_precisao_arbitraria_acima_de_2_53():
    grande = (1 << 53) + 1
    assert calcular_total([(1, grande)], desconto=0, frete=0) == grande

    grande_impar = (1 << 53) + 3
    assert calcular_total([(1, grande_impar)], desconto=0, frete=1) == grande_impar + 1

    bruto_grande = ((1 << 53) + 1) * 100 + 99
    esperado = (bruto_grande * 99) // 100
    assert calcular_total([(1, bruto_grande)], desconto=1, frete=0) == esperado

    q1 = (1 << 30) + 3
    p1 = (1 << 30) + 7
    q2 = 5
    p2 = (1 << 55) + 11
    frete_grande = (1 << 54) + 9
    bruto_total = q1 * p1 + q2 * p2
    esperado_total = (bruto_total * 63) // 100 + frete_grande
    assert calcular_total([(q1, p1), (q2, p2)], desconto=37, frete=frete_grande) == esperado_total


@pytest.mark.parametrize(
    "itens,desconto,frete",
    [
        ([], -1, 0),
        ([], 101, 0),
        ([], 0, -1),
        ([(1, 100)], -1, 0),
        ([(1, 100)], -50, 0),
        ([(1, 100)], 101, 0),
        ([(1, 100)], 200, 0),
        ([(1, 100)], 0, -1),
        ([(3, 200), (1, 50), (2, 100)], -1, 0),
        ([(3, 200), (1, 50), (2, 100)], 101, 0),
        ([(3, 200), (1, 50), (2, 100)], 0, -1),
        ([(0, 100)], 0, -1),
        ([(0, 100)], -1, 0),
        ([(0, 100)], 101, 0),
        ([(-1, 100)], 0, 0),
        ([(-1, 0)], 0, 0),
        ([(1, -1)], 0, 0),
        ([(0, -1)], 0, 0),
        ([(0, -100)], 0, 0),
        ([(5, 100), (-1, 10)], 0, 0),
        ([(5, 100), (1, -10)], 0, 0),
        ([(5, 100), (0, -10)], 0, 0),
        ([(0, 100), (-1, 50)], 0, 0),
        ([(0, 100), (1, -50)], 0, 0),
        ([(0, 0), (0, -1)], 0, 0),
        ([(0, 0), (-1, 0)], 0, 0),
        ([(2, 300), (0, 100), (-1, 50), (1, 20)], 10, 15),
        ([(2, 300), (0, 100), (1, -50), (1, 20)], 10, 15),
    ],
)
def test_validacao_lanca_value_error_e_preserva_lista(itens, desconto, frete):
    copia = list(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=desconto, frete=frete)
    assert itens == copia


def test_lista_nao_alterada_e_chamadas_independentes_inclusive_apos_erro():
    itens = [(3, 200), (0, 500), (1, 100)]
    copia = list(itens)
    assert calcular_total(itens, desconto=10, frete=20) == 650
    assert itens == copia

    # Segunda chamada com outros dados não acumula estado da primeira
    assert calcular_total([(1, 50)], desconto=0, frete=10) == 60
    assert calcular_total([], desconto=0, frete=10) == 0

    # Chamada que falha após processar primeiros itens não contamina chamadas seguintes
    itens_invalidos = [(4, 300), (2, 100), (-1, 50), (1, 100)]
    copia_invalidos = list(itens_invalidos)
    with pytest.raises(ValueError):
        calcular_total(itens_invalidos, desconto=10, frete=50)
    assert itens_invalidos == copia_invalidos

    assert calcular_total([], desconto=0, frete=50) == 0
    assert calcular_total([(0, 100)], desconto=0, frete=50) == 0
    assert calcular_total([(1, 100)], desconto=0, frete=50) == 150
