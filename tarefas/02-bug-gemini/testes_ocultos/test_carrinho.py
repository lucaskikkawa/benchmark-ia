import pytest
from carrinho import CarrinhoDeCompras


def test_instancias_independentes():
    c1 = CarrinhoDeCompras()
    c2 = CarrinhoDeCompras()
    c1.adicionar_item("Livro", 50.0, 1)
    assert [item["nome"] for item in c1.listar_itens()] == ["Livro"]
    assert c2.listar_itens() == []


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
    assert c.listar_itens()[0]["quantidade"] == 3

    # Removendo quantidade igual ou maior que a existente
    c.remover_item("Borracha", 3)
    assert c.listar_itens() == []

    c.adicionar_item("Lápis", 1.0, 2)
    c.remover_item("Lápis")  # None remove tudo
    assert c.listar_itens() == []


def test_remover_quantidade_maior_que_estoque():
    c = CarrinhoDeCompras()
    c.adicionar_item("Livro", 10.0, 2)
    c.remover_item("Livro", 3)
    assert c.listar_itens() == []
    assert c.calcular_total() == 0.0


def test_carrinho_vazio_e_remocao_de_cupom_inexistente():
    c = CarrinhoDeCompras()
    c.remover_cupom()
    assert c.listar_itens() == []
    assert c.calcular_subtotal() == 0.0
    assert c.calcular_desconto() == 0.0
    assert c.calcular_total() == 0.0


def test_cupom_zero_substitui_anterior():
    c = CarrinhoDeCompras()
    c.adicionar_item("Livro", 100.0)
    c.aplicar_cupom("METADE", 50)
    c.aplicar_cupom("ZERO", 0)
    assert c.calcular_desconto() == 0.0
    assert c.calcular_total() == 100.0
    c.aplicar_cupom("NOVO", 25)
    assert c.calcular_total() == 75.0


def test_arredondamento_do_desconto_e_total():
    c = CarrinhoDeCompras()
    c.adicionar_item("A", 0.334)
    c.adicionar_item("B", 0.334)
    assert c.calcular_subtotal() == 0.67
    c.aplicar_cupom("FRACAO", 33)
    assert c.calcular_desconto() == 0.22
    assert c.calcular_total() == 0.45


def test_itens_fornecidos_ao_construtor():
    c = CarrinhoDeCompras({"Livro": {"preco": 12.5, "quantidade": 2}})
    assert c.listar_itens() == [
        {"nome": "Livro", "preco": 12.5, "quantidade": 2, "total": 25.0}
    ]


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


def test_isolamento_profundo_dicionario_construtor():
    dict_externo = {"Caneta": {"preco": 2.5, "quantidade": 2}}
    c = CarrinhoDeCompras(dict_externo)
    # Modificações no dict original ou no dict aninhado não afetam o carrinho
    dict_externo["Caneta"]["preco"] = 999.0
    dict_externo["Caneta"]["quantidade"] = 100
    dict_externo["Novo"] = {"preco": 10.0, "quantidade": 1}

    itens = c.listar_itens()
    assert len(itens) == 1
    assert itens[0]["preco"] == 2.5
    assert itens[0]["quantidade"] == 2
    assert c.calcular_subtotal() == 5.0


def test_isolamento_dicionarios_listar_itens():
    c = CarrinhoDeCompras()
    c.adicionar_item("Lápis", 2.0, 5)
    itens = c.listar_itens()
    # Modifica o dict retornado
    itens[0]["preco"] = 100.0
    itens[0]["quantidade"] = 999
    # Estado interno permanece inalterado
    assert c.calcular_subtotal() == 10.0
    assert c.listar_itens()[0]["preco"] == 2.0


def test_validacao_tipos_adicionar_item():
    c = CarrinhoDeCompras()
    # Tipos incorretos para nome
    with pytest.raises(ValueError):
        c.adicionar_item("", 10.0, 1)
    with pytest.raises(ValueError):
        c.adicionar_item("   ", 10.0, 1)
    with pytest.raises(TypeError):
        c.adicionar_item(123, 10.0, 1)  # type: ignore

    # Tipos incorretos para preco (bool é subclasse de int)
    with pytest.raises(TypeError):
        c.adicionar_item("Item", True, 1)  # type: ignore
    with pytest.raises(TypeError):
        c.adicionar_item("Item", "10.0", 1)  # type: ignore

    # Tipos incorretos para quantidade
    with pytest.raises(TypeError):
        c.adicionar_item("Item", 10.0, 1.5)  # type: ignore
    with pytest.raises(TypeError):
        c.adicionar_item("Item", 10.0, True)  # type: ignore


def test_validacao_tipos_cupom():
    c = CarrinhoDeCompras()
    with pytest.raises(ValueError):
        c.aplicar_cupom("", 10.0)
    with pytest.raises(ValueError):
        c.aplicar_cupom("   ", 10.0)
    with pytest.raises(TypeError):
        c.aplicar_cupom(123, 10.0)  # type: ignore
    with pytest.raises(TypeError):
        c.aplicar_cupom("PROMO", True)  # type: ignore
    with pytest.raises(TypeError):
        c.aplicar_cupom("PROMO", "10")  # type: ignore


def test_remover_item_tipo_quantidade_invalido():
    c = CarrinhoDeCompras()
    c.adicionar_item("Livro", 30.0, 5)
    with pytest.raises(TypeError):
        c.remover_item("Livro", 1.5)  # type: ignore
    with pytest.raises(TypeError):
        c.remover_item("Livro", True)  # type: ignore


def test_ordenacao_unicode_e_acentos():
    c = CarrinhoDeCompras()
    c.adicionar_item("Óleo", 10.0, 1)
    c.adicionar_item("Água", 3.0, 2)
    c.adicionar_item("Café", 15.0, 1)
    c.adicionar_item("Açúcar", 5.0, 2)
    nomes = [it["nome"] for it in c.listar_itens()]
    assert nomes == sorted(["Óleo", "Água", "Café", "Açúcar"])
