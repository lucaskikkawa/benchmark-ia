import unittest

from telefones import extrair_telefones, normalizar_telefone


class TestNormalizarTelefone(unittest.TestCase):
    def test_exemplos_enunciado(self):
        self.assertEqual(normalizar_telefone("+55 (11) 98765-4321"), "+5511987654321")
        self.assertEqual(normalizar_telefone("(21) 3456-7890"), "+552134567890")
        self.assertEqual(normalizar_telefone("11987654321"), "+5511987654321")
        self.assertEqual(normalizar_telefone("( 11 )  98765 - 4321"), "+5511987654321")

    def test_formatos_validos_variados(self):
        self.assertEqual(normalizar_telefone("5511987654321"), "+5511987654321")
        self.assertEqual(normalizar_telefone("55 11 2345-6789"), "+551123456789")
        self.assertEqual(normalizar_telefone("+55.21.4567.8901"), "+552145678901")
        self.assertEqual(normalizar_telefone("(+55) (55) 5123-4567"), "+555551234567")
        self.assertEqual(normalizar_telefone("  55 99123-4567  "), "+5555991234567")
        self.assertEqual(normalizar_telefone("99 90000-0000"), "+5599900000000")

    def test_invalidos_levantam_value_error(self):
        casos_invalidos = [
            "telefone",
            "",
            "   ",
            "()",
            "(11 98765-4321",
            "((11)) 98765-4321",
            "+11 98765-4321",
            "+55 98765-4321",
            "55+11987654321",
            "011 98765-4321",
            "(011) 98765-4321",
            "20 98765-4321",
            "10 3456-7890",
            "11 9876-5432",  # celular com 8 dígitos
            "11 8765-4321",  # fixo começando com 8
            "11 6765-4321",  # fixo começando com 6
            "11 23456-7890",  # 9 dígitos começando com 2
            "11 98765-43210",  # 12 dígitos sem começar com 55
            "55 11 98765-43210",  # 14 dígitos
            "11 98765-4321 ramal 12",
            None,
            11987654321,
        ]
        for caso in casos_invalidos:
            with self.subTest(caso=caso):
                with self.assertRaises(ValueError):
                    normalizar_telefone(caso)  # type: ignore[arg-type]


class TestExtrairTelefones(unittest.TestCase):
    def test_exemplo_enunciado(self):
        self.assertEqual(
            extrair_telefones("Ligar para (11) 98765-4321 ou 21 3456-7890 à tarde"),
            ["+5511987654321", "+552134567890"],
        )

    def test_deduplicacao_e_ordem(self):
        texto = "Principal: +55 (11) 98765-4321; outro: 21 3456-7890; rep: 11987654321"
        self.assertEqual(
            extrair_telefones(texto),
            ["+5511987654321", "+552134567890"],
        )

    def test_separadores_e_pontuacao(self):
        texto = (
            "Contatos: (11) 98765-4321, (21) 3456-7890; +55 31 99999-0000/"
            "41 2345-6789.\n(51 98888-7777)\n11 91111-2222. 21 4444-5555 - 31 5555-6666"
        )
        self.assertEqual(
            extrair_telefones(texto),
            [
                "+5511987654321",
                "+552134567890",
                "+5531999990000",
                "+554123456789",
                "+5551988887777",
                "+5511911112222",
                "+552144445555",
                "+553155556666",
            ],
        )

    def test_ignora_nao_telefones_e_nao_recorta(self):
        texto = (
            "Data 11/09/2021, CPF 119.876.543-21, outro CPF 123.456.789-01, "
            "CEP 01310-100, valor R$ 1198,76, protocolo 1198765432100, "
            "codigo 11-98765-4321-00, prefixo 011 98765-4321, "
            "invalido +5521987654, valido 19 98765-4321."
        )
        self.assertEqual(extrair_telefones(texto), ["+5519987654321"])

    def test_texto_vazio_e_invalido(self):
        self.assertEqual(extrair_telefones(""), [])
        self.assertEqual(extrair_telefones("Sem números aqui."), [])
        with self.assertRaises(ValueError):
            extrair_telefones(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
