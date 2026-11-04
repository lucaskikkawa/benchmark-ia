import os
from pathlib import Path
import sys
import pytest

try:
    from carrinho import calcular_total
except ModuleNotFoundError:
    for _caminho in (os.getcwd(), str(Path(__file__).resolve().parent.parent)):
        if _caminho not in sys.path:
            sys.path.append(_caminho)
    from carrinho import calcular_total


def test_carrinho_vazio_e_defaults():
    itens = []
    assert calcular_total(itens) == 0
    assert calcular_total(itens, 0, 0) == 0
    assert calcular_total(itens=itens, desconto=50, frete=1000) == 0
    assert itens == []


def test_calculo_basico_e_argumentos_padrao():
    itens = [(2, 150), (3, 200)]
    copia = list(itens)
    assert calcular_total(itens) == 900
    assert calcular_total(itens, 10) == 810
    assert calcular_total(itens, frete=50) == 950
    assert calcular_total(itens, 10, 50) == 860
    assert calcular_total(itens=itens, desconto=25, frete=40) == 715
    assert itens == copia


def test_frete_condicionado_a_soma_de_quantidades():
    # Sem unidades -> não cobra frete
    assert calcular_total([], frete=500) == 0
    assert calcular_total([(0, 0)], frete=500) == 0
    assert calcular_total([(0, 100)], frete=500) == 0
    assert calcular_total([(0, 100), (0, 200)], desconto=10, frete=500) == 0

    # Item gratuito com quantidade positiva -> cobra frete
    assert calcular_total([(1, 0)], frete=500) == 500
    assert calcular_total([(3, 0)], desconto=50, frete=500) == 500
    assert calcular_total([(0, 100), (1, 0), (0, 50)], frete=500) == 500

    # Desconto de 100% zera líquido, mas unidades > 0 -> cobra frete integral
    assert calcular_total([(1, 100)], desconto=100, frete=500) == 500
    assert calcular_total([(2, 300)], desconto=100, frete=0) == 0

    # Última linha com quantidade zero não apaga unidades anteriores
    assert calcular_total([(2, 100), (0, 500)], frete=300) == 500
    assert calcular_total([(1, 0), (0, 500)], frete=300) == 300


def test_frete_nao_sofre_desconto():
    assert calcular_total([(1, 1000)], desconto=50, frete=200) == 700
    assert calcular_total([(2, 500)], desconto=100, frete=200) == 200


def test_truncamento_agregado_e_para_baixo():
    # Truncamento agregado (uma vez sobre o bruto) vs truncamento por linha:
    # Por linha: (99 * 50 // 100) * 2 = 49 + 49 = 98
    # Agregado: 198 * 50 // 100 = 99
    assert calcular_total([(1, 99), (1, 99)], desconto=50) == 99
    assert calcular_total([(1, 15), (1, 15)], desconto=10) == 27
    assert calcular_total([(1, 3), (1, 3), (1, 3)], desconto=50) == 4

    # Truncamento para baixo (floor) vs round/ceil:
    # 99 * 50 / 100 = 49.5 -> 49
    assert calcular_total([(1, 99)], desconto=50) == 49
    # 9 * 99 / 100 = 8.91 -> 8
    assert calcular_total([(1, 9)], desconto=1) == 8
    # 99 * 99 / 100 = 98.01 -> 98
    assert calcular_total([(1, 99)], desconto=1) == 98

    # Casos onde float (1 - desconto / 100) erra por imprecisão binária:
    # int(100 * (1 - 7 / 100)) == 92 em float, mas exato é 93
    assert calcular_total([(1, 100)], desconto=7) == 93
    assert calcular_total([(1, 100)], desconto=56) == 44


def test_precisao_arbitraria_acima_de_2_53():
    grande = (1 << 60) + 7
    assert calcular_total([(1, grande)], desconto=0, frete=3) == grande + 3

    preco = (1 << 58) + 101
    esperado = (preco * 99) // 100 + 7
    assert calcular_total([(1, preco)], desconto=1, frete=7) == esperado

    preco_decimal = 10**18 + 3
    assert (
        calcular_total([(1, preco_decimal)], desconto=33, frete=19)
        == (preco_decimal * 67) // 100 + 19
    )

    q = 10**12 + 3
    p = 10**12 + 9
    d = 37
    f = 10**15 + 11
    assert calcular_total([(q, p), (2, p)], desconto=d, frete=f) == (
        ((q + 2) * p * (100 - d)) // 100 + f
    )


@pytest.mark.parametrize("desconto", [-1, -100, 101, 150, 1000])
def test_desconto_invalido_lanca_value_error(desconto):
    itens = [(2, 100), (1, 50)]
    copia = list(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=desconto)
    assert itens == copia

    vazio = []
    with pytest.raises(ValueError):
        calcular_total(vazio, desconto=desconto)
    assert vazio == []

    zeros = [(0, 100)]
    with pytest.raises(ValueError):
        calcular_total(zeros, desconto=desconto)
    assert zeros == [(0, 100)]


def test_bordas_desconto_e_frete_validos():
    assert calcular_total([(1, 250)], desconto=0, frete=0) == 250
    assert calcular_total([(1, 250)], desconto=0, frete=30) == 280
    assert calcular_total([(1, 250)], desconto=100, frete=0) == 0
    assert calcular_total([(1, 250)], desconto=100, frete=30) == 30


@pytest.mark.parametrize("frete", [-1, -50, -1000])
def test_frete_negativo_lanca_value_error(frete):
    itens = [(1, 100)]
    with pytest.raises(ValueError):
        calcular_total(itens, frete=frete)
    assert itens == [(1, 100)]

    # Mesmo em carrinho vazio ou só com quantidade zero
    vazio = []
    with pytest.raises(ValueError):
        calcular_total(vazio, frete=frete)
    assert vazio == []

    zeros = [(0, 100)]
    with pytest.raises(ValueError):
        calcular_total(zeros, frete=frete)
    assert zeros == [(0, 100)]


@pytest.mark.parametrize(
    "itens_invalidos",
    [
        [(-1, 100)],
        [(-1, 0)],
        [(-1, -1)],
        [(0, -1)],
        [(1, -1)],
        [(2, 100), (-1, 50)],
        [(2, 100), (1, -50)],
        [(2, 100), (0, -1)],
        [(0, 100), (-1, 50)],
        [(0, 100), (1, -50)],
        [(0, 100), (0, -1)],
        [(0, 0), (2, 100), (0, 50), (1, -1)],
        [(0, 0), (2, 100), (0, 50), (-1, 1)],
    ],
)
def test_itens_invalidos_lancam_value_error_e_preservam_lista(itens_invalidos):
    copia = list(itens_invalidos)
    with pytest.raises(ValueError):
        calcular_total(itens_invalidos, desconto=10, frete=50)
    assert itens_invalidos == copia


def test_linhas_posteriores_a_quantidade_zero_sao_processadas():
    itens = [(0, 500), (3, 100), (0, 200), (2, 50)]
    copia = list(itens)
    assert calcular_total(itens, desconto=10, frete=40) == 360 + 40
    assert itens == copia


def test_independencia_entre_chamadas_e_apos_erro():
    itens_ok = [(2, 100), (1, 50)]
    assert calcular_total(itens_ok, desconto=10, frete=30) == 255
    assert calcular_total([], desconto=0, frete=30) == 0
    assert calcular_total([(0, 100)], desconto=0, frete=30) == 0

    itens_erro = [(5, 1000), (-1, 100)]
    copia_erro = list(itens_erro)
    with pytest.raises(ValueError):
        calcular_total(itens_erro, desconto=0, frete=500)
    assert itens_erro == copia_erro

    # Chamada seguinte não pode herdar estado parcial da chamada que falhou
    assert calcular_total([], desconto=0, frete=500) == 0
    assert calcular_total([(0, 100)], desconto=0, frete=500) == 0
    assert calcular_total([(1, 100)], desconto=0, frete=500) == 600
    assert calcular_total(itens_ok, desconto=10, frete=30) == 255
    assert itens_ok == [(2, 100), (1, 50)]
