from copy import deepcopy
import pedidos


def linha(categoria='livros', quantidade=1, preco_centavos=100, **extra):
    return dict(categoria=categoria, quantidade=quantidade, preco_centavos=preco_centavos, **extra)


def test_vazio():
    assert pedidos.resumo_pedidos([]) == {'itens': 0, 'total_centavos': 0, 'por_categoria': {}}


def test_simples():
    assert pedidos.resumo_pedidos([linha(quantidade=2)]) == {
        'itens': 2, 'total_centavos': 200, 'por_categoria': {'livros': 200}}


def test_agrega_categorias():
    assert pedidos.resumo_pedidos([linha('A', 2, 10), linha('B', 1, 5), linha('A', 3, 7)]) == {
        'itens': 6, 'total_centavos': 46, 'por_categoria': {'A': 41, 'B': 5}}


def test_desconto_total():
    assert pedidos.resumo_pedidos([linha(desconto_percentual=100)])['total_centavos'] == 0


def test_truncamento_por_linha():
    dados = [linha(quantidade=3, preco_centavos=1, desconto_percentual=50),
             linha(quantidade=1, preco_centavos=1, desconto_percentual=50)]
    assert pedidos.resumo_pedidos(dados)['total_centavos'] == 1


def test_categoria_zerada_preservada():
    assert pedidos.resumo_pedidos([linha('Zero', 0, 9)])['por_categoria'] == {'Zero': 0}


def test_gerador_e_unicode():
    assert pedidos.resumo_pedidos(iter([linha('ação')]))['por_categoria'] == {'ação': 100}


def test_nao_muda_entrada():
    dados = [linha(desconto_percentual=25), linha('A', 2, 3)]
    antes = deepcopy(dados)
    pedidos.resumo_pedidos(dados)
    assert dados == antes


def test_helper_publico():
    assert callable(getattr(pedidos, 'subtotal', None)), 'Crie subtotal em pedidos.py'
    assert pedidos.subtotal(3, 1, 50) == 1
    assert pedidos.subtotal(2, 99) == 198
    assert pedidos.subtotal(5, 12, 100) == 0


def test_delegacao_uma_vez_por_pedido(monkeypatch):
    assert hasattr(pedidos, 'subtotal'), 'Falta a função extraída'
    chamadas = []
    def falso(quantidade, preco_centavos, desconto_percentual=0):
        chamadas.append((quantidade, preco_centavos, desconto_percentual))
        return 17
    monkeypatch.setattr(pedidos, 'subtotal', falso)
    resultado = pedidos.resumo_pedidos([linha('A', 2, 10), linha('B', 0, 8, desconto_percentual=20)])
    assert chamadas == [(2, 10, 0), (0, 8, 20)]
    assert resultado == {'itens': 2, 'total_centavos': 34, 'por_categoria': {'A': 17, 'B': 17}}
