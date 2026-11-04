"""Execute com: python3 -m unittest -v."""

import unittest

from telefones import extrair_telefones, normalizar_telefone


class NormalizacaoTests(unittest.TestCase):
    def test_formatos_validos(self):
        casos = [
            ("+55 (11) 98765-4321", "+5511987654321"),
            ("(21) 3456-7890", "+552134567890"),
            ("11987654321", "+5511987654321"),
            ("55 (21) 3456.7890", "+552134567890"),
            ("55 11 98765 4321", "+5511987654321"),
            ("( 11 )  98765 - 4321", "+5511987654321"),
            ("55 2345-6789", "+555523456789"),
            ("55 98765-4321", "+5555987654321"),
            ("+55 (55) 2345-6789", "+555523456789"),
            ("(+55)..((11))--98765..4321.)", "+5511987654321"),
            ("\t(11)\u00a098765\n4321\t", "+5511987654321"),
            ("99 99999-9999", "+5599999999999"),
        ]
        for entrada, esperado in casos:
            with self.subTest(entrada=entrada):
                self.assertEqual(normalizar_telefone(entrada), esperado)

    def test_formatos_invalidos(self):
        casos = [
            "", "   ()--..", "telefone", "98765-4321", "11 9876-5432",
            "11 19876-5432", "11 88765-4321", "11 6234-5678",
            "11 1234-5678", "11 9345-6789", "11 23456-7890",
            "11 987654-3210", "01 98765-4321", "10 98765-4321",
            "00 2345-6789", "20 3456-7890", "+11 98765-4321",
            "+1 11 98765-4321", "0055 11 98765-4321",
            "0 21 11 98765-4321", "++55 11 98765-4321",
            "55+11 98765-4321", "11/98765-4321", "11,98765-4321",
            "11 98765-4321 ramal 2", "１１９８７６５４３２１", None, 11987654321,
        ]
        for entrada in casos:
            with self.subTest(entrada=entrada):
                with self.assertRaises(ValueError):
                    normalizar_telefone(entrada)

    def test_todos_os_ddds_e_inicios(self):
        for dezena in range(10):
            for unidade in range(10):
                ddd = f"{dezena}{unidade}"
                for inicio in range(10):
                    for tamanho in (8, 9):
                        numero = str(inicio) + "1" * (tamanho - 1)
                        valido = (
                            dezena != 0 and unidade != 0
                            and ((tamanho == 8 and inicio in (2, 3, 4, 5))
                                 or (tamanho == 9 and inicio == 9))
                        )
                        with self.subTest(ddd=ddd, numero=numero):
                            if valido:
                                self.assertEqual(
                                    normalizar_telefone(ddd + numero),
                                    "+55" + ddd + numero,
                                )
                            else:
                                with self.assertRaises(ValueError):
                                    normalizar_telefone(ddd + numero)


class ExtracaoTests(unittest.TestCase):
    def test_exemplo(self):
        self.assertEqual(
            extrair_telefones("Ligar para (11) 98765-4321 ou 21 3456-7890 à tarde"),
            ["+5511987654321", "+552134567890"],
        )

    def test_delimitadores_pontuacao_e_duplicatas(self):
        texto = (
            "+55 (11) 98765-4321.,(21) 3456-7890);"
            "(31) 2345-6789/41 99999-9999\r\n"
            "(51) 5432-1098\n11 98765-4321 ou 552134567890."
        )
        self.assertEqual(extrair_telefones(texto), [
            "+5511987654321", "+552134567890", "+553123456789",
            "+5541999999999", "+555154321098",
        ])

    def test_invalidos_nao_impedem_validos(self):
        self.assertEqual(
            extrair_telefones(
                "Data 29/10/2026, CPF 123.456.789-00; CEP 12345-678; "
                "R$ 1.234,56; código 012345678901234; inválido (20) 3456-7890; "
                "válido (21) 3456-7890."
            ),
            ["+552134567890"],
        )

    def test_nao_recorta_sequencias_maiores(self):
        casos = [
            "011987654321", "119876543210", "55119876543210",
            "0 (11) 98765-4321", "(11) 98765-4321 0",
            "11987654321 2134567890", "11987654321.2134567890",
            "١11987654321", "11987654321１", "+1 11 98765-4321",
            "++55 11 98765-4321", "55+11 98765-4321",
        ]
        for entrada in casos:
            with self.subTest(entrada=entrada):
                self.assertEqual(extrair_telefones(entrada), [])

    def test_identificadores_e_fronteiras(self):
        casos = [
            "id11987654321", "11987654321abc", "_11987654321",
            "11987654321_", "á11987654321", "id+5511987654321",
        ]
        for entrada in casos:
            with self.subTest(entrada=entrada):
                self.assertEqual(extrair_telefones(entrada), [])
        self.assertEqual(
            extrair_telefones("tel:11987654321!"), ["+5511987654321"]
        )

    def test_quebras_de_linha_delimitam(self):
        for quebra in ("\n", "\r", "\r\n", "\u2028"):
            with self.subTest(quebra=repr(quebra)):
                self.assertEqual(
                    extrair_telefones("11987654321" + quebra + "2134567890"),
                    ["+5511987654321", "+552134567890"],
                )
                self.assertEqual(extrair_telefones("11" + quebra + "987654321"), [])

    def test_sobreposicao_com_outros_dados(self):
        self.assertEqual(
            extrair_telefones("119.876.543-21; R$ 11987654321,00"),
            ["+5511987654321"],
        )

    def test_vazios_e_tipo_invalido(self):
        for entrada in ("", " \n()--..", "sem números"):
            self.assertEqual(extrair_telefones(entrada), [])
        for entrada in (None, 11987654321):
            with self.assertRaises(ValueError):
                extrair_telefones(entrada)


if __name__ == "__main__":
    unittest.main()
