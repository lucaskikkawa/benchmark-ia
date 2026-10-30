import unittest
from copy import deepcopy

from carrinho import CarrinhoDeCompras


class CarrinhoDeComprasTests(unittest.TestCase):
    def setUp(self):
        self.carrinho = CarrinhoDeCompras()

    def test_instancias_e_dados_iniciais_sao_isolados(self):
        origem = {"Caderno": {"preco": 15.5, "quantidade": 2}}
        primeiro = CarrinhoDeCompras(origem)
        segundo = CarrinhoDeCompras(origem)
        origem["Caderno"]["preco"] = 99
        origem["Caneta"] = {"preco": 2, "quantidade": 1}
        primeiro.adicionar_item("Caderno", 10, 1)
        self.assertEqual(segundo.listar_itens(), [
            {"nome": "Caderno", "preco": 15.5, "quantidade": 2, "total": 31.0}
        ])
        self.carrinho.adicionar_item("Caneta", 2)
        self.assertEqual(CarrinhoDeCompras().listar_itens(), [])

    def test_adicionar_acumula_quantidade_e_atualiza_preco(self):
        self.carrinho.adicionar_item("Caderno", 15.5, 2)
        self.carrinho.adicionar_item("Caderno", 12)
        self.assertEqual(self.carrinho.listar_itens(), [
            {"nome": "Caderno", "preco": 12, "quantidade": 3, "total": 36}
        ])

    def test_validacao_de_nome_e_codigo(self):
        for metodo in (self.carrinho.adicionar_item, self.carrinho.aplicar_cupom):
            for valor in (None, 1, True, [], {}):
                with self.subTest(metodo=metodo.__name__, valor=valor):
                    with self.assertRaises(TypeError):
                        metodo(valor, 10)
            for valor in ("", " ", "\t\n"):
                with self.subTest(metodo=metodo.__name__, valor=valor):
                    with self.assertRaises(ValueError):
                        metodo(valor, 10)

    def test_validacao_de_preco(self):
        for preco in (True, False, "10", None, [], complex(1, 2)):
            with self.subTest(preco=preco), self.assertRaises(TypeError):
                self.carrinho.adicionar_item("Caderno", preco)
        for preco in (0, -1, -0.5, float("nan")):
            with self.subTest(preco=preco), self.assertRaises(ValueError):
                self.carrinho.adicionar_item("Caderno", preco)
        self.assertEqual(self.carrinho.listar_itens(), [])

    def test_validacao_de_quantidade_preserva_estado(self):
        self.carrinho.adicionar_item("Caderno", 10, 3)
        original = deepcopy(self.carrinho.itens)
        for quantidade in (True, False, 1.0, "1", [], 0, -1):
            erro = ValueError if type(quantidade) is int else TypeError
            for operacao in (
                lambda: self.carrinho.adicionar_item("Caderno", 20, quantidade),
                lambda: self.carrinho.remover_item("Caderno", quantidade),
            ):
                with self.subTest(quantidade=quantidade), self.assertRaises(erro):
                    operacao()
                self.assertEqual(self.carrinho.itens, original)
        with self.assertRaises(TypeError):
            self.carrinho.adicionar_item("Caderno", 20, None)

    def test_remocao_parcial_completa_e_item_ausente(self):
        self.carrinho.adicionar_item("Caderno", 10, 3)
        self.carrinho.remover_item("Caderno", 1)
        self.assertEqual(self.carrinho.itens["Caderno"]["quantidade"], 2)
        for quantidade in (None, 2, 10):
            with self.subTest(quantidade=quantidade):
                carrinho = CarrinhoDeCompras(self.carrinho.itens)
                carrinho.remover_item("Caderno", quantidade)
                self.assertEqual(carrinho.listar_itens(), [])
        with self.assertRaises(KeyError):
            self.carrinho.remover_item("Ausente")

    def test_cupom_limites_substituicao_e_remocao(self):
        self.carrinho.adicionar_item("Caderno", 15.5, 2)
        for porcentagem, desconto, total in (
            (10, 3.1, 27.9), (12.5, 3.88, 27.12), (0, 0.0, 31.0), (100, 31.0, 0.0)
        ):
            with self.subTest(porcentagem=porcentagem):
                self.carrinho.aplicar_cupom(str(porcentagem), porcentagem)
                self.assertEqual(self.carrinho.calcular_desconto(), desconto)
                self.assertEqual(self.carrinho.calcular_total(), total)
        self.carrinho.remover_cupom()
        self.carrinho.remover_cupom()
        self.assertEqual(self.carrinho.calcular_desconto(), 0.0)
        self.assertEqual(self.carrinho.calcular_total(), 31.0)

    def test_desconto_invalido_preserva_cupom(self):
        self.carrinho.aplicar_cupom("VALIDO", 10)
        for porcentagem in (True, False, "10", None, [], -1, 101, float("nan")):
            erro = (ValueError if type(porcentagem) in (int, float) else TypeError)
            with self.subTest(porcentagem=porcentagem), self.assertRaises(erro):
                self.carrinho.aplicar_cupom("INVALIDO", porcentagem)
            self.assertEqual(self.carrinho.cupom_desconto,
                             {"codigo": "VALIDO", "porcentagem": 10})

    def test_arredondamento_e_carrinho_vazio(self):
        self.assertEqual(self.carrinho.calcular_subtotal(), 0.0)
        self.assertEqual(self.carrinho.calcular_total(), 0.0)
        self.carrinho.aplicar_cupom("DEZ", 10)
        self.assertEqual(self.carrinho.calcular_desconto(), 0.0)
        self.carrinho.adicionar_item("Produto", 1.234, 3)
        self.assertEqual(self.carrinho.calcular_subtotal(), 3.7)
        self.assertEqual(self.carrinho.calcular_desconto(), 0.37)
        self.assertEqual(self.carrinho.calcular_total(), 3.33)
        self.assertEqual(self.carrinho.listar_itens()[0]["total"], 3.7)

    def test_listagem_ordenada_e_isolada(self):
        nomes = ["Água", "caderno", "Zebra", "Caneta", "ábaco", " Caderno "]
        for nome in nomes:
            self.carrinho.adicionar_item(nome, 2)
        lista = self.carrinho.listar_itens()
        self.assertEqual([item["nome"] for item in lista], sorted(nomes))
        lista[0]["preco"] = 99
        lista[0]["quantidade"] = 99
        lista.clear()
        self.assertEqual(len(self.carrinho.listar_itens()), len(nomes))
        self.assertEqual(self.carrinho.calcular_subtotal(), 12.0)


if __name__ == "__main__":
    unittest.main()
