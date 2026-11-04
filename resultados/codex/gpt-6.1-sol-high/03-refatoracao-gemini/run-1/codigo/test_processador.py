import unittest

from processador import (
    CalculadoraDesconto,
    CalculadoraFrete,
    ItemPedido,
    Pedido,
    processar_pedidos,
)


class ProcessadorTests(unittest.TestCase):
    def test_item_padroes_e_quantidade(self):
        item = ItemPedido("Livro", 12.345, quantidade=3)
        self.assertEqual(item.subtotal, 37.04)
        self.assertEqual(item.peso_total, 1.5)
        self.assertEqual(ItemPedido("Livro", 10).quantidade, 1)

    def test_validacoes_dos_itens(self):
        for campos in ({"preco": -1}, {"quantidade": 0}, {"peso_kg": -0.1}):
            with self.subTest(campos=campos), self.assertRaises(ValueError):
                ItemPedido(**{"nome": "Item", "preco": 0, **campos})
        self.assertEqual(ItemPedido("Grátis", 0, peso_kg=0).subtotal, 0)

    def test_arredondamento_por_item(self):
        pedido = Pedido(
            "1", "Ana", itens=[ItemPedido("Item", 0.006, peso_kg=0.0006)] * 3
        )
        self.assertEqual(pedido.calcular_total_itens(), 0.03)
        self.assertEqual(pedido.calcular_peso_total(), 0.003)

    def test_fretes_e_limite_de_gratuidade(self):
        for tipo, esperado in (("PaDrAo", 13.0), ("EXPRESSO", 31.0), ("economico", 6.6)):
            with self.subTest(tipo=tipo):
                self.assertEqual(CalculadoraFrete.calcular(tipo, 2, 199.99), esperado)
                self.assertEqual(CalculadoraFrete.calcular(tipo, 2, 200), 0.0)
        self.assertEqual(CalculadoraFrete.calcular("desconhecido", 2, 200), 0.0)
        with self.assertRaisesRegex(ValueError, "Tipo de frete desconhecido: OUTRO"):
            CalculadoraFrete.calcular("OUTRO", 0, 0)

    def test_validacoes_das_calculadoras(self):
        for peso, valor in ((-1, 0), (0, -1), (-1, 200)):
            with self.subTest(peso=peso, valor=valor), self.assertRaises(ValueError):
                CalculadoraFrete.calcular("padrao", peso, valor)
        with self.assertRaises(ValueError):
            CalculadoraDesconto.calcular("bronze", -1)

    def test_categorias_e_limites_de_desconto(self):
        casos = [
            ("bronze", 100, 0.0),
            ("PRATA", 99.99, 0.0),
            ("prata", 100, 5.0),
            ("ouro", 49.99, 2.5),
            ("OuRo", 50, 5.0),
            ("VIP", 10, 1.5),
            ("outra", 100, 0.0),
        ]
        for categoria, valor, esperado in casos:
            with self.subTest(categoria=categoria, valor=valor):
                self.assertEqual(CalculadoraDesconto.calcular(categoria, valor), esperado)

    def test_pedidos_vazios_e_ordem(self):
        self.assertEqual(processar_pedidos([]), [])
        resultados = processar_pedidos([
            {"id": "2", "cliente": "Ana"},
            {"id": "1", "cliente": "Bia", "itens": [], "tipo_frete": "expresso"},
        ])
        self.assertEqual(resultados, [
            {"id": "2", "cliente": "Ana", "subtotal": 0.0, "desconto": 0.0,
             "frete": 10.0, "total": 10.0},
            {"id": "1", "cliente": "Bia", "subtotal": 0.0, "desconto": 0.0,
             "frete": 25.0, "total": 25.0},
        ])
        self.assertIsInstance(resultados[0]["subtotal"], float)

    def test_listas_de_itens_independentes(self):
        primeiro = Pedido("1", "Ana")
        segundo = Pedido("2", "Bia")
        primeiro.itens.append(ItemPedido("Item", 10))
        self.assertEqual(segundo.itens, [])

    def test_processamento_completo_e_frete_antes_do_desconto(self):
        dados = [{
            "id": "1", "cliente": "Ana", "categoria_cliente": "VIP",
            "itens": [{"nome": "Livro", "preco": "100", "quantidade": "2"}],
        }]
        self.assertEqual(processar_pedidos(dados), [{
            "id": "1", "cliente": "Ana", "subtotal": 200.0,
            "desconto": 30.0, "frete": 0.0, "total": 170.0,
        }])
        self.assertEqual(dados[0]["itens"][0]["preco"], "100")


if __name__ == "__main__":
    unittest.main()
