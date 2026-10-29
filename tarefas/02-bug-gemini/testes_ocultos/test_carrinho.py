import pytest
from carrinho import CarrinhoDeCompras


def test_instancias_independentes():
    c1 = CarrinhoDeCompras()
    c2 = CarrinhoDeCompras()
    c1.adicionar_item("Livro", 50.0, 1)
    assert "Livro" in c1.itens
    assert "Livro" not in c2.itens
    assert len(c2.itens) == 0


def test_adicionar_item_valido_e_atualizacao():
    c = CarrinhoDeCompras()
    c.adicionar_item("Caneta", 2.50, 2)
    assert c.calcular_subtotal() == 5.0
    # Adicionar novamente atualiza preço e soma quantidade
    c.adicionar_item("Caneta", 3.00, 3)
    itens = c.listar_itens()
    assert len(itens) == 1
    assert itens[0]["quantidade"] == 5
    assert itens[0]["preco"] == 3.0
    assert itens[0]["total"] == 15.0


def test_adicionar_item_valores_invalidos():
    c = CarrinhoDeCompras()
    with pytest.raises(ValueError):
        c.adicionar_item("Item", 0.0, 1)
    with pytest.raises(ValueError):
        c.adicionar_item("Item", -10.0, 1)
    with pytest.raises(ValueError):
        c.adicionar_item("Item", 10.0, 0)
    with pytest.raises(ValueError):
        c.adicionar_item("Item", 10.0, -2)


def test_remover_item_parcial_e_total():
    c = CarrinhoDeCompras()
    c.adicionar_item("Borracha", 1.50, 5)
    c.remover_item("Borracha", 2)
    assert c.itens["Borracha"]["quantidade"] == 3

    # Removendo quantidade igual ou maior que a existente
    c.remover_item("Borracha", 3)
    assert "Borracha" not in c.itens

    c.adicionar_item("Lápis", 1.0, 2)
    c.remover_item("Lápis")  # None remove tudo
    assert "Lápis" not in c.itens


def test_remover_item_erros():
    c = CarrinhoDeCompras()
    with pytest.raises(KeyError):
        c.remover_item("Inexistente")
    c.adicionar_item("Régua", 4.0, 1)
    with pytest.raises(ValueError):
        c.remover_item("Régua", 0)
    with pytest.raises(ValueError):
        c.remover_item("Régua", -1)


def test_aplicar_e_remover_cupom():
    c = CarrinhoDeCompras()
    c.adicionar_item("Mochila", 100.0, 1)
    c.aplicar_cupom("PROMO10", 10.0)
    assert c.calcular_subtotal() == 100.0
    assert c.calcular_desconto() == 10.0
    assert c.calcular_total() == 90.0

    c.remover_cupom()
    assert c.calcular_desconto() == 0.0
    assert c.calcular_total() == 100.0


def test_cupom_valores_invalidos():
    c = CarrinhoDeCompras()
    with pytest.raises(ValueError):
        c.aplicar_cupom("INVALIDO", -5.0)
    with pytest.raises(ValueError):
        c.aplicar_cupom("INVALIDO", 100.1)


def test_arredondamento_e_desconto_100():
    c = CarrinhoDeCompras()
    c.adicionar_item("Item 1", 10.333, 1)
    c.adicionar_item("Item 2", 20.333, 2)
    # subtotal: 10.333 + 40.666 = 50.999 -> arredonda para 51.0
    assert c.calcular_subtotal() == 51.0
    c.aplicar_cupom("GRATIS", 100.0)
    assert c.calcular_total() == 0.0


def test_listar_itens_ordenacao_alfabetica():
    c = CarrinhoDeCompras()
    c.adicionar_item("Zebra de Pelúcia", 50.0, 1)
    c.adicionar_item("Apontador", 5.0, 2)
    c.adicionar_item("Caderno", 15.0, 3)
    itens = c.listar_itens()
    nomes = [item["nome"] for item in itens]
    assert nomes == ["Apontador", "Caderno", "Zebra de Pelúcia"]
