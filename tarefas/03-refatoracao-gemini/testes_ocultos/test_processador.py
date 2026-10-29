import pytest
from processador import (
    CalculadoraDesconto,
    CalculadoraFrete,
    ItemPedido,
    Pedido,
    processar_pedidos,
)


def valor_item(item, atributo):
    valor = getattr(item, atributo)
    return valor() if callable(valor) else valor


def test_item_pedido_calculos():
    item = ItemPedido(nome="Teclado", preco=150.0, quantidade=2, peso_kg=0.8)
    assert valor_item(item, "subtotal") == 300.0
    assert valor_item(item, "peso_total") == 1.6


def test_item_pedido_validacoes():
    with pytest.raises(ValueError):
        ItemPedido(nome="Invalido", preco=-10.0, quantidade=1, peso_kg=1.0)
    with pytest.raises(ValueError):
        ItemPedido(nome="Invalido", preco=10.0, quantidade=0, peso_kg=1.0)
    with pytest.raises(ValueError):
        ItemPedido(nome="Invalido", preco=10.0, quantidade=-2, peso_kg=1.0)
    with pytest.raises(ValueError):
        ItemPedido(nome="Invalido", preco=10.0, quantidade=1, peso_kg=-0.5)


def test_calculadora_frete_tipos_e_gratis():
    assert CalculadoraFrete.calcular("padrao", 2.0, 250.0) == 0.0
    assert CalculadoraFrete.calcular("expresso", 5.0, 200.0) == 0.0

    assert CalculadoraFrete.calcular("padrao", 2.0, 100.0) == 13.0
    assert CalculadoraFrete.calcular("expresso", 2.0, 100.0) == 31.0
    assert CalculadoraFrete.calcular("economico", 2.0, 100.0) == 6.6


def test_calculadora_frete_tipo_invalido():
    with pytest.raises(ValueError):
        CalculadoraFrete.calcular("aereo_rapido", 1.0, 50.0)


def test_calculadora_frete_valores_negativos():
    with pytest.raises(ValueError):
        CalculadoraFrete.calcular("padrao", -1.0, 50.0)
    with pytest.raises(ValueError):
        CalculadoraFrete.calcular("padrao", 1.0, -10.0)


def test_calculadora_desconto_categorias():
    assert CalculadoraDesconto.calcular("bronze", 500.0) == 0.0
    assert CalculadoraDesconto.calcular("prata", 80.0) == 0.0
    assert CalculadoraDesconto.calcular("prata", 100.0) == 5.0
    assert CalculadoraDesconto.calcular("ouro", 40.0) == 2.0
    assert CalculadoraDesconto.calcular("ouro", 100.0) == 10.0
    assert CalculadoraDesconto.calcular("vip", 100.0) == 15.0


def test_calculadora_desconto_valor_negativo():
    with pytest.raises(ValueError):
        CalculadoraDesconto.calcular("ouro", -50.0)


def test_pedido_estrutura_e_totais():
    itens = [
        ItemPedido(nome="Mouse", preco=50.0, quantidade=1, peso_kg=0.2),
        ItemPedido(nome="Mousepad", preco=30.0, quantidade=1, peso_kg=0.3),
    ]
    p = Pedido(
        id="PED-1",
        cliente="Ana",
        categoria_cliente="ouro",
        itens=itens,
        tipo_frete="padrao",
    )
    assert p.calcular_total_itens() == 80.0
    assert p.calcular_peso_total() == 0.5
    assert p.calcular_desconto() == 8.0
    assert p.calcular_frete() == 10.75
    assert p.calcular_total_final() == 82.75

    d = p.para_dict()
    assert d == {
        "id": "PED-1",
        "cliente": "Ana",
        "subtotal": 80.0,
        "desconto": 8.0,
        "frete": 10.75,
        "total": 82.75,
    }


def test_processar_pedidos_multiplos():
    pedidos_raw = [
        {
            "id": "1",
            "cliente": "Carlos",
            "categoria_cliente": "vip",
            "tipo_frete": "expresso",
            "itens": [{"nome": "Monitor", "preco": 300.0, "quantidade": 1, "peso_kg": 4.0}],
        },
        {
            "id": "2",
            "cliente": "Beatriz",
            "categoria_cliente": "bronze",
            "tipo_frete": "economico",
            "itens": [{"nome": "Cabo", "preco": 20.0, "quantidade": 2, "peso_kg": 0.1}],
        },
    ]

    resultado = processar_pedidos(pedidos_raw)
    assert len(resultado) == 2

    assert resultado[0]["subtotal"] == 300.0
    assert resultado[0]["desconto"] == 45.0
    assert resultado[0]["frete"] == 0.0
    assert resultado[0]["total"] == 255.0

    assert resultado[1]["subtotal"] == 40.0
    assert resultado[1]["desconto"] == 0.0
    assert resultado[1]["frete"] == 5.16
    assert resultado[1]["total"] == 45.16


def test_processar_pedidos_lista_vazia():
    assert processar_pedidos([]) == []


def test_processar_pedidos_valores_padrao():
    pedidos_raw = [
        {
            "id": "3",
            "cliente": "Daniel",
            "itens": [{"nome": "Livro", "preco": 50.0}],
        }
    ]
    res = processar_pedidos(pedidos_raw)
    assert len(res) == 1
    assert res[0]["subtotal"] == 50.0
    assert res[0]["desconto"] == 0.0
    assert res[0]["frete"] == 10.75
    assert res[0]["total"] == 60.75


def test_item_padrao_e_arredondamento():
    item = ItemPedido(nome="A", preco=1.234, quantidade=3, peso_kg=0.12345)
    assert valor_item(item, "subtotal") == 3.7
    assert valor_item(item, "peso_total") == 0.37
    padrao = ItemPedido(nome="B", preco=2.0)
    assert padrao.quantidade == 1
    assert padrao.peso_kg == 0.5


def test_pedidos_vazios_e_listas_independentes():
    p1 = Pedido(id="1", cliente="A")
    p2 = Pedido(id="2", cliente="B")
    assert p1.para_dict() == {
        "id": "1", "cliente": "A", "subtotal": 0.0,
        "desconto": 0.0, "frete": 10.0, "total": 10.0,
    }
    p1.itens.append(ItemPedido(nome="X", preco=10))
    assert p2.itens == []
    assert processar_pedidos([{"id": "2", "cliente": "B"}]) == [p2.para_dict()]


@pytest.mark.parametrize("categoria,valor,esperado", [
    ("PrAtA", 99.99, 0.0), ("PRATA", 100.0, 5.0),
    ("OuRo", 49.0, 2.45), ("OURO", 50.0, 5.0),
    ("VIP", 1.0, 0.15), ("desconhecida", 100.0, 0.0),
])
def test_categorias_limites_e_maiusculas(categoria, valor, esperado):
    assert CalculadoraDesconto.calcular(categoria, valor) == esperado


def test_frete_limite_maiusculas_e_arredondamento():
    assert CalculadoraFrete.calcular("PaDrAo", 0.123, 199.99) == 10.18
    assert CalculadoraFrete.calcular("EXPRESSO", 0.123, 199.99) == 25.37
    assert CalculadoraFrete.calcular("ECONOMICO", 0.123, 199.99) == 5.1
    assert CalculadoraFrete.calcular("inexistente", 10.0, 200.0) == 0.0
    with pytest.raises(ValueError) as exc:
        CalculadoraFrete.calcular("inexistente", 10.0, 199.99)
    assert "inexistente" in str(exc.value)


def test_pedido_delega_calculos(monkeypatch):
    chamadas = []

    def desconto(categoria, valor):
        chamadas.append(("desconto", categoria, valor))
        return 7.0

    def frete(tipo, peso, valor):
        chamadas.append(("frete", tipo, peso, valor))
        return 8.0

    monkeypatch.setattr(CalculadoraDesconto, "calcular", staticmethod(desconto))
    monkeypatch.setattr(CalculadoraFrete, "calcular", staticmethod(frete))
    pedido = Pedido(id="1", cliente="A", categoria_cliente="vip", tipo_frete="expresso",
                    itens=[ItemPedido(nome="X", preco=12.5, quantidade=2, peso_kg=0.2)])
    assert pedido.calcular_desconto() == 7.0
    assert pedido.calcular_frete() == 8.0
    assert ("desconto", "vip", 25.0) in chamadas
    assert ("frete", "expresso", 0.4, 25.0) in chamadas


def test_arredondamento_por_item_vs_soma_global():
    # 100 itens com preço 1.004 e quantidade 1
    # Cada item subtotal: round(1.004 * 1, 2) = 1.00
    # Soma dos subtotais dos itens = 100.00
    # Se alguém calcular round(sum(1.004 * 100), 2) = round(100.4, 2) = 100.40 (errado!)
    itens = [ItemPedido(nome=f"Item {i}", preco=1.004, quantidade=1, peso_kg=0.01) for i in range(100)]
    pedido = Pedido(id="ARRED-1", cliente="Cliente Teste", itens=itens)
    assert pedido.calcular_total_itens() == 100.00


def test_arredondamento_de_peso_por_item_antes_de_somar():
    itens = [ItemPedido(nome="X", preco=1.0, peso_kg=0.0004) for _ in range(100)]
    pedido = Pedido(id="PESO", cliente="A", itens=itens)
    assert pedido.calcular_peso_total() == 0.0


def test_pedidos_com_unicode_e_volume():
    pedidos = [
        {
            "id": f"PED-{i:04d}",
            "cliente": f"Usuário Especial {i} çãé",
            "categoria_cliente": "vip",
            "tipo_frete": "padrao",
            "itens": [
                {"nome": "Café Gourmet", "preco": 25.5, "quantidade": 2, "peso_kg": 0.25},
                {"nome": "Açúcar Mascavo", "preco": 10.0, "quantidade": 1, "peso_kg": 1.0},
            ],
        }
        for i in range(50)
    ]
    res = processar_pedidos(pedidos)
    assert len(res) == 50
    assert res[0]["cliente"] == "Usuário Especial 0 çãé"
    # subtotal = 51.0 + 10.0 = 61.0
    # desconto vip 15% de 61.0 = 9.15
    # peso = 0.5 + 1.0 = 1.5 kg
    # frete padrao = 10 + 1.5 * 1.5 = 12.25
    # total = 61.0 - 9.15 + 12.25 = 64.10
    assert res[0]["subtotal"] == 61.0
    assert res[0]["desconto"] == 9.15
    assert res[0]["frete"] == 12.25
    assert res[0]["total"] == 64.10
