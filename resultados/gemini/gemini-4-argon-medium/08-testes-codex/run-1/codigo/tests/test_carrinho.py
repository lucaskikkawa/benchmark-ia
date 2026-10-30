import pytest

try:
    from carrinho import calcular_total
except ModuleNotFoundError:
    import pathlib
    import sys

    sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))
    from carrinho import calcular_total


def test_carrinho_vazio_e_defaults():
    itens = []
    assert calcular_total(itens) == 0
    assert calcular_total(itens, 0, 0) == 0
    assert calcular_total(itens, desconto=50, frete=1000) == 0
    assert itens == []


def test_calculo_basico_e_multiplos_itens():
    itens = [(2, 1500), (3, 500)]
    resultado = calcular_total(itens)
    assert type(resultado) is int
    assert resultado == 4500
    assert itens == [(2, 1500), (3, 500)]


def test_desconto_aplicado_uma_vez_no_bruto_com_truncamento():
    # Truncamento para baixo (floor), diferente de round() e de bruto - (bruto * d // 100)
    # 10 * 99 // 100 = 9 (enquanto round daria 10 e 10 - (10*1//100) daria 10)
    assert calcular_total([(1, 10)], desconto=1) == 9

    # Truncamento agregado entre linhas e unidades:
    # Bruto = 30 + 30 = 60; 60 * 95 // 100 = 57 (por linha seria 28 + 28 = 56)
    assert calcular_total([(1, 30), (1, 30)], desconto=5) == 57
    assert calcular_total([(2, 30)], desconto=5) == 57
    assert calcular_total([(1, 33), (1, 33), (1, 34)], desconto=1) == 99


def test_bordas_de_desconto():
    itens = [(2, 1234)]
    assert calcular_total(itens, desconto=0, frete=100) == 2568
    assert calcular_total(itens, desconto=100, frete=0) == 0
    assert calcular_total(itens, desconto=100, frete=350) == 350


def test_regras_de_frete_e_quantidades_zero():
    # Frete não sofre desconto
    assert calcular_total([(1, 1000)], desconto=50, frete=200) == 700

    # Quantidade zero não paga frete (mesmo com itens na lista e preço > 0)
    assert calcular_total([(0, 1000)], desconto=0, frete=500) == 0
    assert calcular_total([(0, 1000), (0, 2000)], desconto=10, frete=500) == 0

    # Item gratuito com quantidade positiva paga frete (bruto == 0, unidades > 0)
    assert calcular_total([(1, 0)], desconto=0, frete=500) == 500
    assert calcular_total([(2, 0)], desconto=50, frete=500) == 500

    # Combinação de linhas com quantidade zero e positiva (antes e depois)
    assert calcular_total([(0, 1000), (2, 300)], desconto=0, frete=150) == 750
    assert calcular_total([(2, 300), (0, 1000)], desconto=0, frete=150) == 750
    assert calcular_total([(0, 1000), (1, 0), (0, 500)], desconto=0, frete=150) == 150


def test_precisao_arbitraria_acima_de_2_pow_53():
    grande = (1 << 53) + 1
    assert calcular_total([(1, grande)], desconto=0, frete=0) == grande
    assert calcular_total([(1, grande)], desconto=0, frete=7) == grande + 7

    preco_enorme = (1 << 65) + 1234567890123456789
    q1, q2 = 7, 13
    desconto = 17
    frete = 987654321
    bruto = (q1 + q2) * preco_enorme
    esperado = (bruto * (100 - desconto)) // 100 + frete
    resultado = calcular_total([(q1, preco_enorme), (q2, preco_enorme)], desconto=desconto, frete=frete)
    assert type(resultado) is int
    assert resultado == esperado


@pytest.mark.parametrize("desconto_invalido", [-1, -100, 101, 150])
def test_desconto_invalido_lanca_value_error(desconto_invalido):
    itens = [(1, 100)]
    copia = list(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=desconto_invalido, frete=0)
    assert itens == copia

    # Mesmo com carrinho vazio ou quantidade zero
    vazio = []
    with pytest.raises(ValueError):
        calcular_total(vazio, desconto=desconto_invalido, frete=0)
    assert vazio == []

    zeros = [(0, 0)]
    with pytest.raises(ValueError):
        calcular_total(zeros, desconto=desconto_invalido, frete=0)
    assert zeros == [(0, 0)]


@pytest.mark.parametrize("frete_invalido", [-1, -500])
def test_frete_invalido_lanca_value_error(frete_invalido):
    itens = [(1, 100)]
    copia = list(itens)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=0, frete=frete_invalido)
    assert itens == copia

    # Mesmo em carrinho vazio ou quantidade zero (onde frete não seria cobrado)
    vazio = []
    with pytest.raises(ValueError):
        calcular_total(vazio, desconto=0, frete=frete_invalido)
    assert vazio == []

    zeros = [(0, 100)]
    with pytest.raises(ValueError):
        calcular_total(zeros, desconto=0, frete=frete_invalido)
    assert zeros == [(0, 100)]


@pytest.mark.parametrize(
    "itens_invalidos",
    [
        [(-1, 100)],
        [(-1, 0)],
        [(1, -1)],
        [(0, -1)],
        [(5, 100), (-1, 100)],
        [(0, 100), (-1, 100)],
        [(0, 100), (1, -1)],
        [(0, 100), (0, -1)],
        [(0, 0), (2, 50), (0, -5)],
    ],
)
def test_itens_invalidos_lancam_value_error_e_preservam_lista(itens_invalidos):
    itens = list(itens_invalidos)
    with pytest.raises(ValueError):
        calcular_total(itens, desconto=0, frete=100)
    assert itens == itens_invalidos

    with pytest.raises(ValueError):
        calcular_total(itens, desconto=100, frete=0)
    assert itens == itens_invalidos


def test_independencia_entre_chamadas_e_apos_erro():
    assert calcular_total([(2, 500)], desconto=10, frete=100) == 1000

    itens_erro = [(3, 1000), (-1, 200)]
    with pytest.raises(ValueError):
        calcular_total(itens_erro, desconto=0, frete=50)
    assert itens_erro == [(3, 1000), (-1, 200)]

    # Chamadas subsequentes não devem acumular bruto ou unidades da chamada anterior
    assert calcular_total([], desconto=0, frete=50) == 0
    assert calcular_total([(0, 500)], desconto=0, frete=50) == 0
    assert calcular_total([(1, 200)], desconto=0, frete=50) == 250
