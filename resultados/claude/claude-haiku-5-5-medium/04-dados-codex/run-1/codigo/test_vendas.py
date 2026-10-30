import json
import sys
import tempfile
import unittest
from pathlib import Path

from vendas import resumir_vendas


class ResumirVendasTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)

    def tearDown(self):
        self._tmp.cleanup()

    def _csv(self, conteudo, nome="entrada.csv", encoding="utf-8"):
        caminho = self.dir / nome
        caminho.write_bytes(conteudo.encode(encoding) if isinstance(conteudo, str) else conteudo)
        return caminho

    def _saida(self):
        return self.dir / "saida.json"

    def test_agrega_filtra_e_ordena(self):
        entrada = self._csv(
            "status,produto,quantidade,preco_centavos,extra\n"
            "Pago , Café ,2,100,x\n"
            "pago,Café,1,50,\n"
            "cancelado,Café,9,999,\n"
            "pago,Chá,0,300,\n"
            "pago,chá,1,10,\n"
        )
        saida = self._saida()
        resultado = resumir_vendas(entrada, saida)
        esperado = [
            {"produto": "Café", "quantidade": 3, "receita_centavos": 250},
            {"produto": "Chá", "quantidade": 0, "receita_centavos": 0},
            {"produto": "chá", "quantidade": 1, "receita_centavos": 10},
        ]
        self.assertEqual(resultado, esperado)
        self.assertEqual(json.loads(saida.read_text(encoding="utf-8")), esperado)
        self.assertTrue(saida.read_text(encoding="utf-8").endswith("\n"))

    def test_minimo_filtra_apos_agregacao(self):
        entrada = self._csv("produto,quantidade,preco_centavos,status\nA,1,5,pago\nA,1,5,pago\nB,1,9,pago\n")
        resultado = resumir_vendas(entrada, self._saida(), 10)
        self.assertEqual(resultado, [{"produto": "A", "quantidade": 2, "receita_centavos": 10}])

    def test_bom_e_acentos_sem_escape(self):
        entrada = self._csv("﻿produto,quantidade,preco_centavos,status\nAçúcar \"cru\",1,1,pago\n")
        saida = self._saida()
        resumir_vendas(entrada, saida)
        texto = saida.read_text(encoding="utf-8")
        self.assertIn("Açúcar", texto)
        self.assertNotIn("\\u", texto)

    def test_numeros_aceitos_e_rejeitados(self):
        cabecalho = "produto,quantidade,preco_centavos,status\n"
        ok = self._csv(cabecalho + "A,+007, -0 ,pago\n")
        self.assertEqual(resumir_vendas(ok, self._saida()), [{"produto": "A", "quantidade": 7, "receita_centavos": 0}])
        for ruim in ["1_0", "1.5", "1e3", "٣", "-1", "", "x"]:
            with self.subTest(valor=ruim):
                entrada = self._csv(cabecalho + f"A,{ruim},1,pago\n")
                with self.assertRaises(ValueError):
                    resumir_vendas(entrada, self._saida())

    def test_grande_exato(self):
        grande = "9" * 5000
        entrada = self._csv(f"produto,quantidade,preco_centavos,status\nA,{grande},{grande},pago\n")
        resultado = resumir_vendas(entrada, self._saida())
        limite = sys.get_int_max_str_digits()
        sys.set_int_max_str_digits(0)
        try:
            esperado = int(grande) ** 2
        finally:
            sys.set_int_max_str_digits(limite)
        self.assertEqual(resultado[0]["receita_centavos"], esperado)

    def test_erro_preserva_saida_anterior(self):
        saida = self._saida()
        saida.write_text("antigo\n", encoding="utf-8")
        entrada = self._csv("produto,quantidade,preco_centavos,status\nA,1,1,pago\nB,x,1,pago\n")
        with self.assertRaises(ValueError):
            resumir_vendas(entrada, saida)
        self.assertEqual(saida.read_text(encoding="utf-8"), "antigo\n")

    def test_validacoes_de_cabecalho_e_parametros(self):
        saida = self._saida()
        with self.assertRaises(ValueError):
            resumir_vendas(self._csv(""), saida)
        with self.assertRaises(ValueError):
            resumir_vendas(self._csv("produto,quantidade,status\n"), saida)
        entrada = self._csv("produto,quantidade,preco_centavos,status\n")
        self.assertEqual(resumir_vendas(entrada, saida), [])
        self.assertEqual(saida.read_text(encoding="utf-8"), "[]\n")
        for minimo in [-1, True, 1.0, "1", None]:
            with self.subTest(minimo=minimo):
                with self.assertRaises(ValueError):
                    resumir_vendas(entrada, saida, minimo)

    def test_linhas_incompletas(self):
        entrada = self._csv("produto,quantidade,preco_centavos,status\nA,1\nB,1,2,pendente\n")
        self.assertEqual(resumir_vendas(entrada, self._saida()), [])
        entrada = self._csv("status,produto,quantidade,preco_centavos\npago,A,1\n")
        with self.assertRaises(ValueError):
            resumir_vendas(entrada, self._saida())

    def test_produto_vazio_e_aspas_preservadas(self):
        with self.assertRaises(ValueError):
            resumir_vendas(self._csv("produto,quantidade,preco_centavos,status\n  ,1,1,pago\n"), self._saida())
        entrada = self._csv('produto,quantidade,preco_centavos,status\n"linha\n  um",1,1,pago\n')
        resultado = resumir_vendas(entrada, self._saida())
        self.assertEqual(resultado[0]["produto"], "linha\n  um")

    def test_entrada_e_saida_iguais_rejeitadas(self):
        entrada = self._csv("produto,quantidade,preco_centavos,status\nA,1,1,pago\n")
        with self.assertRaises(ValueError):
            resumir_vendas(entrada, entrada)


if __name__ == "__main__":
    unittest.main()
