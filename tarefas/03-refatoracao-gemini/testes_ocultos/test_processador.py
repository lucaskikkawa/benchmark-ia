import pytest
from processador import (
    CalculadoraDesconto,
    CalculadoraFrete,
    ItemPedido,
    Pedido,
    processar_pedidos,
)


def valor_item(item, atributo):
    # O enunciado permite tanto propriedades quanto métodos.
    valor = getattr(item, atributo)
    return valor() if callable(valor) else valor


def test_item_pedido_calculos():
    item = ItemPedido(nome="Teclado", preco=150.0, quantidade=2, peso_kg=0.8)
    assert valor_item(item, "subtotal") == 300.0
    assert valor_item(item, "peso_total") == 1.6


def test_calculadora_frete_tipos_e_gratis():
    # Frete grátis para valor_total >= 200
    assert CalculadoraFrete.calcular("padrao", 2.0, 250.0) == 0.0
    assert CalculadoraFrete.calcular("expresso", 5.0, 200.0) == 0.0

    # Frete padrão: 10 + peso * 1.5
    assert CalculadoraFrete.calcular("padrao", 2.0, 100.0) == 13.0
    # Frete expresso: 25 + peso * 3.0
    assert CalculadoraFrete.calcular("expresso", 2.0, 100.0) == 31.0
    # Frete economico: 5 + peso * 0.8
    assert CalculadoraFrete.calcular("economico", 2.0, 100.0) == 6.6


def test_calculadora_frete_tipo_invalido():
    with pytest.raises(ValueError):
        CalculadoraFrete.calcular("aereo_rapido", 1.0, 50.0)


def test_calculadora_desconto_categorias():
    # Bronze: 0
    assert CalculadoraDesconto.calcular("bronze", 500.0) == 0.0
    # Prata: 5% apenas se >= 100
    assert CalculadoraDesconto.calcular("prata", 80.0) == 0.0
    assert CalculadoraDesconto.calcular("prata", 100.0) == 5.0
    # Ouro: 10% se >= 50, senão 5%
    assert CalculadoraDesconto.calcular("ouro", 40.0) == 2.0
    assert CalculadoraDesconto.calcular("ouro", 100.0) == 10.0
    # VIP: 15% sempre
    assert CalculadoraDesconto.calcular("vip", 100.0) == 15.0


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
    # total itens: 80.0
    assert p.calcular_total_itens() == 80.0
    # peso total: 0.5 kg
    assert p.calcular_peso_total() == 0.5
    # desconto ouro >= 50: 10% de 80 = 8.0
    assert p.calcular_desconto() == 8.0
    # frete padrao: 10 + 0.5 * 1.5 = 10.75
    assert p.calcular_frete() == 10.75
    # total final: 80 - 8 + 10.75 = 82.75
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

    # Pedido 1: subtotal 300.0 >= 200 => frete 0.0. VIP 15% de 300 = 45.0. total = 255.0
    assert resultado[0]["subtotal"] == 300.0
    assert resultado[0]["desconto"] == 45.0
    assert resultado[0]["frete"] == 0.0
    assert resultado[0]["total"] == 255.0

    # Pedido 2: subtotal 40.0. bronze => desconto 0.0. peso = 0.2 kg. economico = 5 + 0.2*0.8 = 5.16. total = 45.16
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
            "itens": [{"nome": "Livro", "preco": 50.0}],  # sem quantidade nem peso_kg
        }
    ]
    res = processar_pedidos(pedidos_raw)
    assert len(res) == 1
    assert res[0]["subtotal"] == 50.0
    # categoria padrao bronze => desc 0.0
    assert res[0]["desconto"] == 0.0
    # tipo frete padrao padrao => 10 + 0.5 * 1.5 = 10.75
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
    assert str(exc.value) == "Tipo de frete desconhecido: inexistente"


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
    assert chamadas == [("desconto", "vip", 25.0), ("frete", "expresso", 0.4, 25.0)]


def test_soma_de_subtotais_e_pesos_arredondados_por_item():
    itens = [ItemPedido(nome=nome, preco=0.334, peso_kg=0.12345) for nome in ("A", "B")]
    pedido = Pedido(id="1", cliente="A", itens=itens)
    assert pedido.calcular_total_itens() == 0.66
    assert pedido.calcular_peso_total() == pytest.approx(0.246)
    bruto = {"id": "1", "cliente": "A", "itens": [
        {"nome": nome, "preco": 0.334, "peso_kg": 0.12345} for nome in ("A", "B")
    ]}
    assert processar_pedidos([bruto]) == [pedido.para_dict()]
