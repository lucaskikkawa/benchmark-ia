from copy import deepcopy
import random
import pytest
import pedidos


@pytest.mark.parametrize('quantidade,preco,desconto', [
    (10**90 + 3, 10**65 + 7, 1), (3, 10**120 + 1, 99),
    (0, 10**100, 37), (9, 0, 73), (10**80, 77, 100),
    (3, 1, 50), (17, 13, 33),
])
def test_subtotal_exato(quantidade, preco, desconto):
    assert callable(getattr(pedidos, 'subtotal', None)), 'Falta subtotal público'
    resultado = pedidos.subtotal(quantidade, preco, desconto)
    assert type(resultado) is int
    assert resultado == quantidade * preco * (100-desconto) // 100


def test_delegacao_ordenada_usa_cada_retorno(monkeypatch):
    assert hasattr(pedidos, 'subtotal'), 'Falta subtotal público'
    dados = [
        {'categoria': ' A ', 'quantidade': 0, 'preco_centavos': 0},
        {'categoria': 'B', 'quantidade': 2, 'preco_centavos': 7, 'desconto_percentual': 100},
        {'categoria': ' A ', 'quantidade': 2, 'preco_centavos': 7},
        {'categoria': 'zero', 'quantidade': 0, 'preco_centavos': 1, 'desconto_percentual': 1},
    ]
    antes, chamadas = deepcopy(dados), []
    retornos = iter([13, 10**75 + 1, 29, 0])

    def falso(quantidade, preco_centavos, desconto_percentual=0):
        chamadas.append((quantidade, preco_centavos, desconto_percentual))
        return next(retornos)

    monkeypatch.setattr(pedidos, 'subtotal', falso)
    assert pedidos.resumo_pedidos((linha for linha in dados)) == {
        'itens': 4, 'total_centavos': 10**75 + 43,
        'por_categoria': {' A ': 42, 'B': 10**75 + 1, 'zero': 0}}
    assert chamadas == [(0, 0, 0), (2, 7, 100), (2, 7, 0), (0, 1, 1)]
    assert dados == antes
    assert pedidos.resumo_pedidos(iter(())) == {
        'itens': 0, 'total_centavos': 0, 'por_categoria': {}}
    assert len(chamadas) == 4


def test_oraculo_volume_categorias_exatas_e_chamadas_independentes():
    rng = random.Random(963)
    categorias = ['', ' ', 'A', 'a', 'á', 'a\u0301', 'ação\n', '🧪']
    dados, esperado = [], {'itens': 0, 'total_centavos': 0, 'por_categoria': {}}
    for i in range(4000):
        categoria = categorias[i % len(categorias)]
        quantidade, preco = rng.randrange(6), 10**70 + rng.randrange(1000)
        desconto = rng.randrange(101)
        dados.append(dict(categoria=categoria, quantidade=quantidade,
                          preco_centavos=preco, desconto_percentual=desconto))
        valor = quantidade * preco * (100-desconto) // 100
        esperado['itens'] += quantidade
        esperado['total_centavos'] += valor
        esperado['por_categoria'][categoria] = esperado['por_categoria'].get(categoria, 0) + valor
    antes = deepcopy(dados)
    primeiro = pedidos.resumo_pedidos(iter(dados))
    assert primeiro == esperado and dados == antes
    primeiro['por_categoria'].clear()
    assert pedidos.resumo_pedidos(iter(dados)) == esperado
