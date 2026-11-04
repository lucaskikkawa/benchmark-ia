import json
import os
import shutil
import tempfile
import unittest
from pathlib import Path

from vendas import resumir_vendas


class TestResumirVendas(unittest.TestCase):
    def setUp(self):
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_basic_flow(self):
        csv_content = (
            "produto,quantidade,preco_centavos,status\n"
            "Camiseta,2,2500,pago\n"
            "Calça,1,5000,pendente\n"
            "Camiseta,1,2500,PAGO\n"
        )
        entrada = Path(self.test_dir) / "vendas.csv"
        saida = Path(self.test_dir) / "resumo.json"
        entrada.write_text(csv_content, encoding="utf-8")

        res = resumir_vendas(entrada, saida)
        expected = [
            {"produto": "Camiseta", "quantidade": 3, "receita_centavos": 7500}
        ]
        self.assertEqual(res, expected)
        self.assertTrue(saida.exists())
        with open(saida, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertTrue(content.endswith("\n"))
            self.assertEqual(json.loads(content), expected)

    def test_bom_support(self):
        csv_content = (
            "\ufeffstatus,preco_centavos,produto,quantidade\n"
            "pago,100,Maçã,5\n"
        )
        entrada = Path(self.test_dir) / "bom.csv"
        saida = Path(self.test_dir) / "bom.json"
        entrada.write_text(csv_content, encoding="utf-8")

        res = resumir_vendas(str(entrada), str(saida))
        self.assertEqual(res, [{"produto": "Maçã", "quantidade": 5, "receita_centavos": 500}])
        # Check accents not escaped
        with open(saida, "r", encoding="utf-8") as f:
            raw = f.read()
            self.assertIn("Maçã", raw)
            self.assertNotIn("\\u", raw)

    def test_empty_csv_raises_value_error(self):
        entrada = Path(self.test_dir) / "empty.csv"
        saida = Path(self.test_dir) / "out.json"
        entrada.write_text("", encoding="utf-8")

        with self.assertRaises(ValueError):
            resumir_vendas(entrada, saida)
        self.assertFalse(saida.exists())

    def test_only_header_returns_empty_list(self):
        entrada = Path(self.test_dir) / "header_only.csv"
        saida = Path(self.test_dir) / "out.json"
        entrada.write_text("produto,quantidade,preco_centavos,status\n", encoding="utf-8")

        res = resumir_vendas(entrada, saida)
        self.assertEqual(res, [])
        self.assertEqual(json.loads(saida.read_text(encoding="utf-8")), [])

    def test_missing_required_column(self):
        entrada = Path(self.test_dir) / "missing_col.csv"
        saida = Path(self.test_dir) / "out.json"
        entrada.write_text("produto,quantidade,status\nA,1,pago\n", encoding="utf-8")

        with self.assertRaises(ValueError):
            resumir_vendas(entrada, saida)
        self.assertFalse(saida.exists())

    def test_minimo_centavos_validation(self):
        entrada = Path(self.test_dir) / "valid.csv"
        saida = Path(self.test_dir) / "out.json"
        entrada.write_text("produto,quantidade,preco_centavos,status\nA,1,100,pago\n", encoding="utf-8")

        for invalid in [-1, -100, True, False, 1.5, "100", None]:
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    resumir_vendas(entrada, saida, minimo_centavos=invalid)
                self.assertFalse(saida.exists())

    def test_minimo_centavos_filtering(self):
        csv_content = (
            "produto,quantidade,preco_centavos,status\n"
            "Barato,1,50,pago\n"
            "Médio,1,100,pago\n"
            "Caro,1,200,pago\n"
        )
        entrada = Path(self.test_dir) / "filter.csv"
        saida = Path(self.test_dir) / "out.json"
        entrada.write_text(csv_content, encoding="utf-8")

        res = resumir_vendas(entrada, saida, minimo_centavos=100)
        self.assertEqual(
            res,
            [
                {"produto": "Caro", "quantidade": 1, "receita_centavos": 200},
                {"produto": "Médio", "quantidade": 1, "receita_centavos": 100},
            ],
        )

    def test_zero_quantity_product_preserved(self):
        csv_content = (
            "produto,quantidade,preco_centavos,status\n"
            "ZeroQtd,0,500,pago\n"
        )
        entrada = Path(self.test_dir) / "zero.csv"
        saida = Path(self.test_dir) / "out.json"
        entrada.write_text(csv_content, encoding="utf-8")

        res = resumir_vendas(entrada, saida, minimo_centavos=0)
        self.assertEqual(res, [{"produto": "ZeroQtd", "quantidade": 0, "receita_centavos": 0}])

    def test_numbers_syntax(self):
        # Valid syntaxes: +123, 007, -0, +0
        csv_content = (
            "produto,quantidade,preco_centavos,status\n"
            "A,+005,010,pago\n"
            "B,+0,-0,pago\n"
        )
        entrada = Path(self.test_dir) / "syntax.csv"
        saida = Path(self.test_dir) / "out.json"
        entrada.write_text(csv_content, encoding="utf-8")

        res = resumir_vendas(entrada, saida)
        self.assertEqual(
            res,
            [
                {"produto": "A", "quantidade": 5, "receita_centavos": 50},
                {"produto": "B", "quantidade": 0, "receita_centavos": 0},
            ],
        )

    def test_invalid_numbers_raise_value_error(self):
        invalid_nums = ["1.0", "1e3", "1_000", "-5", "abc", "", "   ", "१२३"]
        for num in invalid_nums:
            with self.subTest(num=num):
                entrada = Path(self.test_dir) / f"invalid_{hash(num)}.csv"
                saida = Path(self.test_dir) / "out.json"
                entrada.write_text(
                    f"produto,quantidade,preco_centavos,status\nA,{num},100,pago\n",
                    encoding="utf-8",
                )
                with self.assertRaises(ValueError):
                    resumir_vendas(entrada, saida)
                self.assertFalse(saida.exists())

    def test_unpaid_rows_ignored_before_validation(self):
        # Unpaid rows with broken numbers, missing columns, empty product should be ignored!
        csv_content = (
            "produto,quantidade,preco_centavos,status\n"
            "Valid,1,100,pago\n"
            ",invalid_num,-50,pendente\n"
            "BrokenRow\n"
            ",,,cancelado\n"
        )
        entrada = Path(self.test_dir) / "unpaid_broken.csv"
        saida = Path(self.test_dir) / "out.json"
        entrada.write_text(csv_content, encoding="utf-8")

        res = resumir_vendas(entrada, saida)
        self.assertEqual(res, [{"produto": "Valid", "quantidade": 1, "receita_centavos": 100}])

    def test_empty_product_in_paid_row_raises(self):
        csv_content = (
            "produto,quantidade,preco_centavos,status\n"
            "   ,1,100,pago\n"
        )
        entrada = Path(self.test_dir) / "empty_prod.csv"
        saida = Path(self.test_dir) / "out.json"
        entrada.write_text(csv_content, encoding="utf-8")

        with self.assertRaises(ValueError):
            resumir_vendas(entrada, saida)
        self.assertFalse(saida.exists())

    def test_quoted_product_with_newlines_and_quotes(self):
        csv_content = (
            'produto,quantidade,preco_centavos,status\n'
            '"Produto ""Especial""\nCom Linha 2",2,100,pago\n'
        )
        entrada = Path(self.test_dir) / "quoted.csv"
        saida = Path(self.test_dir) / "out.json"
        entrada.write_text(csv_content, encoding="utf-8")

        res = resumir_vendas(entrada, saida)
        expected_prod = 'Produto "Especial"\nCom Linha 2'
        self.assertEqual(res[0]["produto"], expected_prod)

    def test_exact_big_integers_beyond_64bits(self):
        big_q = 10**25
        big_p = 10**25
        csv_content = f"produto,quantidade,preco_centavos,status\nBig,{big_q},{big_p},pago\n"
        entrada = Path(self.test_dir) / "big.csv"
        saida = Path(self.test_dir) / "out.json"
        entrada.write_text(csv_content, encoding="utf-8")

        res = resumir_vendas(entrada, saida)
        self.assertEqual(res[0]["receita_centavos"], big_q * big_p)

    def test_previous_output_intact_on_value_error(self):
        entrada = Path(self.test_dir) / "bad.csv"
        saida = Path(self.test_dir) / "intact.json"
        entrada.write_text("produto,quantidade,preco_centavos,status\nA,invalid,100,pago\n", encoding="utf-8")
        saida.write_text("ORIGINAL CONTENT", encoding="utf-8")

        with self.assertRaises(ValueError):
            resumir_vendas(entrada, saida)

        self.assertEqual(saida.read_text(encoding="utf-8"), "ORIGINAL CONTENT")

    def test_large_dataset_performance(self):
        entrada = Path(self.test_dir) / "large.csv"
        saida = Path(self.test_dir) / "large.json"
        lines = ["extra,produto,quantidade,preco_centavos,status\n"]
        for i in range(30000):
            lines.append(f"ignorar,Prod_{i % 100},{i % 5},{i % 1000},pago\n")
        entrada.write_text("".join(lines), encoding="utf-8")

        res = resumir_vendas(entrada, saida)
        self.assertEqual(len(res), 100)
        self.assertTrue(saida.exists())


if __name__ == "__main__":
    unittest.main()
