import unittest
from copy import deepcopy

from carrinho import CarrinhoDeCompras


class TestCarrinhoDeCompras(unittest.TestCase):
    def test_isolamento_das_instancias_e_dos_dados_iniciais(self):
        primeiro = CarrinhoDeCompras()
        segundo = CarrinhoDeCompras()
        primeiro.adicionar_item("Caderno", 15.5)
        self.assertEqual(segundo.itens, {})

        origem = {"Caderno": {"preco": 15.5, "quantidade": 2}}
        carrinho = CarrinhoDeCompras(origem)
        origem["Caderno"]["preco"] = 100
        origem.clear()
        self.assertEqual(carrinho.calcular_subtotal(), 31.0)

    def test_adicao_acumula_quantidade_e_atualiza_preco(self):
        carrinho = CarrinhoDeCompras()
        carrinho.adicionar_item("Caderno", 15.5, 2)
        carrinho.adicionar_item("Caderno", 20)
        self.assertEqual(carrinho.itens["Caderno"], {"preco": 20, "quantidade": 3})

    def test_validacoes_na_adicao_preservam_estado(self):
        carrinho = CarrinhoDeCompras({"Caderno": {"preco": 15.5, "quantidade": 2}})
        anterior = deepcopy(carrinho.itens)
        casos = [
            ((None, 10, 1), TypeError),
            ((123, 10, 1), TypeError),
            (("", 10, 1), ValueError),
            ((" \t\n", 10, 1), ValueError),
        ]
        casos += [(("Caderno", valor, 1), TypeError) for valor in (True, False, "10", None)]
        casos += [(("Caderno", valor, 1), ValueError) for valor in (0, -1, float("nan"))]
        casos += [(("Caderno", 10, valor), TypeError) for valor in (True, False, 1.0, "1", None)]
        casos += [(("Caderno", 10, valor), ValueError) for valor in (0, -1)]
        for argumentos, erro in casos:
            with self.subTest(argumentos=argumentos):
                with self.assertRaises(erro):
                    carrinho.adicionar_item(*argumentos)
                self.assertEqual(carrinho.itens, anterior)

    def test_remocao_parcial_e_completa(self):
        for quantidade in (None, 2, 3):
            with self.subTest(quantidade=quantidade):
                carrinho = CarrinhoDeCompras({"A": {"preco": 10, "quantidade": 3}})
                carrinho.remover_item("A", 1)
                self.assertEqual(carrinho.itens["A"]["quantidade"], 2)
                carrinho.remover_item("A", quantidade)
                self.assertEqual(carrinho.itens, {})
        with self.assertRaises(KeyError):
            carrinho.remover_item("ausente")

    def test_validacoes_na_remocao(self):
        carrinho = CarrinhoDeCompras({"A": {"preco": 10, "quantidade": 3}})
        for valor, erro in [(True, TypeError), (False, TypeError), (1.0, TypeError),
                            ("1", TypeError), (0, ValueError), (-1, ValueError)]:
            with self.subTest(valor=valor):
                with self.assertRaises(erro):
                    carrinho.remover_item("A", valor)
                self.assertEqual(carrinho.itens["A"]["quantidade"], 3)

    def test_cupons_arredondamento_substituicao_e_remocao(self):
        carrinho = CarrinhoDeCompras()
        self.assertEqual(carrinho.calcular_subtotal(), 0.0)
        self.assertEqual(carrinho.calcular_total(), 0.0)
        self.assertEqual(carrinho.calcular_desconto(), 0.0)
        carrinho.adicionar_item("A", 10.125, 3)
        self.assertEqual(carrinho.calcular_subtotal(), 30.38)
        for percentual in (0, 12.5, 100):
            carrinho.aplicar_cupom("PROMO", percentual)
            desconto = round(30.38 * (percentual / 100), 2)
            self.assertEqual(carrinho.calcular_desconto(), desconto)
            self.assertEqual(carrinho.calcular_total(), round(30.38 - desconto, 2))
        carrinho.remover_cupom()
        carrinho.remover_cupom()
        self.assertEqual(carrinho.calcular_total(), 30.38)

    def test_validacoes_do_cupom_preservam_cupom_anterior(self):
        carrinho = CarrinhoDeCompras()
        carrinho.aplicar_cupom("VALIDO", 20)
        casos = [(None, 10, TypeError), (1, 10, TypeError),
                 ("", 10, ValueError), (" \t", 10, ValueError)]
        casos += [("NOVO", valor, TypeError) for valor in (True, False, None, "10")]
        casos += [("NOVO", valor, ValueError) for valor in (-1, 101, float("nan"))]
        for codigo, percentual, erro in casos:
            with self.subTest(codigo=codigo, percentual=percentual):
                with self.assertRaises(erro):
                    carrinho.aplicar_cupom(codigo, percentual)
                self.assertEqual(carrinho.cupom_desconto, {"codigo": "VALIDO", "porcentagem": 20})

    def test_listagem_ordenada_e_independente(self):
        carrinho = CarrinhoDeCompras()
        nomes = ["Água", "Zebra", "Caderno", "banana", "arroz"]
        for nome in nomes:
            carrinho.adicionar_item(nome, 15.5, 2)
        itens = carrinho.listar_itens()
        self.assertEqual([item["nome"] for item in itens], sorted(nomes))
        self.assertEqual(itens[0], {"nome": "Caderno", "preco": 15.5, "quantidade": 2, "total": 31.0})
        itens[0]["preco"] = 999
        itens.clear()
        self.assertEqual(len(carrinho.listar_itens()), 5)
        self.assertEqual(carrinho.itens["Caderno"]["preco"], 15.5)


if __name__ == "__main__":
    unittest.main()
