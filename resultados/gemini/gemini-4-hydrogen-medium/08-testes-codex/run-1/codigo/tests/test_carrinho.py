import pytest

from carrinho import calcular_total


def test_carrinho_vazio_sem_frete_e_com_frete():
    assert calcular_total([]) == 0
    assert calcular_total([], desconto=0, frete=0) == 0
    assert calcular_total([], desconto=25, frete=500) == 0


def test_padroes_e_argumentos_nomeados():
    assert calcular_total([(2, 150)]) == 300
    assert calcular_total([(2, 150)], 10) == 270
    assert calcular_total([(2, 150)], frete=50) == 350
    assert calcular_total([(2, 150)], desconto=10, frete=50) == 320


def test_multiplos_itens_soma_quantidade_vezes_preco():
    itens = [(2, 350), (3, 200), (1, 150)]
    assert calcular_total(itens) == 1450
    assert calcular_total(itens, desconto=10, frete=250) == 1555


def test_frete_sem_desconto_e_regra_de_unidades_positivas():
    # Desconto incide apenas sobre o bruto, nunca sobre o frete
    assert calcular_total([(1, 100)], desconto=50, frete=200) == 250
    assert calcular_total([(2, 500)], desconto=100, frete=300) == 300

    # Item gratuito com quantidade positiva paga frete
    assert calcular_total([(1, 0)], frete=500) == 500
    assert calcular_total([(0, 1000), (2, 0)], desconto=50, frete=500) == 500

    # Linhas com quantidade zero nao pagam frete
    assert calcular_total([(0, 500)], frete=500) == 0
    assert calcular_total([(0, 0), (0, 999)], desconto=10, frete=500) == 0


def test_truncamento_para_baixo_e_agregado_entre_linhas():
    # Truncamento para baixo (nao arredonda para cima em .5 ou .9)
    assert calcular_total([(1, 11)], desconto=10) == 9
    assert calcular_total([(1, 15)], desconto=10) == 13

    # Desconto aplicado uma vez sobre o bruto agregado, nao por linha
    assert calcular_total([(1, 5), (1, 5)], desconto=10) == 9
    assert calcular_total([(1, 3), (1, 3), (1, 4)], desconto=10) == 9
    assert calcular_total([(1, 1), (1, 1), (1, 1)], desconto=33) == 2


@pytest.mark.parametrize("desconto", [0, 1, 99, 100])
def test_bordas_validas_desconto(desconto):
    esperado = 1000 * (100 - desconto) // 100
    assert calcular_total([(1, 1000)], desconto=desconto) == esperado


@pytest.mark.parametrize("desconto", [-1, -100, 101, 200])
def test_desconto_invalido_lanca_value_error(desconto):
    with pytest.raises(ValueError):
        calcular_total([(1, 100)], desconto=desconto)
    with pytest.raises(ValueError):
        calcular_total([], desconto=desconto)


def test_frete_invalido_lanca_value_error():
    assert calcular_total([(1, 100)], frete=0) == 100
    with pytest.raises(ValueError):
        calcular_total([(1, 100)], frete=-1)
    with pytest.raises(ValueError):
        calcular_total([], frete=-1)


@pytest.mark.parametrize(
    "itens",
    [
        [(-1, 0)],
        [(-1, 100)],
        [(0, -1)],
        [(1, -1)],
        [(0, 100), (0, -1)],
        [(0, 100), (-1, 100)],
        [(2, 100), (0, -5)],
        [(2, 100), (-1, 0)],
    ],
)
def test_itens_invalidos_incluindo_apos_quantidade_zero(itens):
    with pytest.raises(ValueError):
        calcular_total(itens)


def test_precisao_arbitraria_acima_de_2_pow_53():
    grande = 2**53 + 1
    assert calcular_total([(1, grande)]) == grande
    assert calcular_total([(1, grande)], desconto=0, frete=1) == grande + 1

    muito_grande = 2**64 + 123456789012345
    esperado = (3 * muito_grande) * (100 - 7) // 100 + 19
    assert calcular_total([(3, muito_grande)], desconto=7, frete=19) == esperado


def test_lista_nao_alterada_e_chamadas_independentes():
    itens_validos = [(2, 150), (0, 50), (1, 300)]
    copia_valida = list(itens_validos)
    assert calcular_total(itens_validos, desconto=10, frete=50) == 590
    assert itens_validos == copia_valida

    itens_invalidos = [(1, 100), (0, -5)]
    copia_invalida = list(itens_invalidos)
    with pytest.raises(ValueError):
        calcular_total(itens_invalidos, desconto=10, frete=50)
    assert itens_invalidos == copia_invalida

    itens_desconto_errado = [(2, 200)]
    with pytest.raises(ValueError):
        calcular_total(itens_desconto_errado, desconto=101, frete=50)
    assert itens_desconto_errado == [(2, 200)]

    # Chamadas subsequentes apos erro continuam independentes e corretas
    assert calcular_total([(1, 200)], desconto=10, frete=30) == 210
    assert calcular_total([]) == 0
