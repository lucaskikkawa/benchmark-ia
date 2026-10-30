import json
import os
import tempfile
import unittest

from analisador_vendas import processar_vendas

CABECALHO = "id_transacao,data,cliente,categoria,valor,status\n"


class ProcessarVendasTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name

    def tearDown(self):
        self._tmp.cleanup()

    def _csv(self, conteudo: str, nome: str = "vendas.csv", encoding: str = "utf-8") -> str:
        caminho = os.path.join(self.dir, nome)
        with open(caminho, "w", encoding=encoding, newline="") as f:
            f.write(conteudo)
        return caminho

    def _saida(self, *partes: str) -> str:
        return os.path.join(self.dir, *partes)

    def test_arquivo_inexistente(self):
        with self.assertRaises(FileNotFoundError):
            processar_vendas(os.path.join(self.dir, "nao_existe.csv"), self._saida("o.json"))

    def test_diretorio_nao_e_arquivo(self):
        with self.assertRaises(FileNotFoundError):
            processar_vendas(self.dir, self._saida("o.json"))

    def test_top_n_tipo_invalido(self):
        caminho = self._csv(CABECALHO)
        for valor in (2.0, "3", True, None):
            with self.subTest(valor=valor), self.assertRaises(TypeError):
                processar_vendas(caminho, self._saida("o.json"), top_n=valor)

    def test_top_n_menor_que_um(self):
        caminho = self._csv(CABECALHO)
        for valor in (0, -1):
            with self.subTest(valor=valor), self.assertRaises(ValueError):
                processar_vendas(caminho, self._saida("o.json"), top_n=valor)

    def test_arquivo_vazio_retorna_metricas_zeradas(self):
        caminho = self._csv("")
        resultado = processar_vendas(caminho, self._saida("o.json"))
        self.assertEqual(
            resultado,
            {
                "total_transacoes": 0,
                "receita_total": 0.0,
                "ticket_medio": 0.0,
                "por_categoria": {},
                "top_clientes": [],
            },
        )

    def test_metricas_completas_com_filtros_e_bom(self):
        conteudo = (
            "﻿ id_transacao , data,  cliente ,categoria,valor,status\n"
            "1,2024-01-01,  Ana ,Eletronicos,100.10, Concluido \n"
            "2,2024-01-02,Bruno,Casa,50.00,concluido\n"
            "3,2024-01-03,Ana,Casa,25.25,CONCLUIDO\n"
            "4,2024-01-04,Carla,Casa,999.00,cancelado\n"
            "5,2024-01-05,Bruno,Eletronicos,-10,concluido\n"
            "6,2024-01-06,Diego,Eletronicos,abc,concluido\n"
            "7,2024-01-07,Diego,Eletronicos,nan,concluido\n"
            "\n"
            "8,2024-01-08,,Casa,10,concluido\n"
            "9,2024-01-09,Eva,Casa,0,concluido\n"
        )
        caminho = self._csv(conteudo, encoding="utf-8")
        saida = self._saida("sub", "dir", "resultado.json")

        resultado = processar_vendas(caminho, saida)

        self.assertEqual(resultado["total_transacoes"], 4)
        self.assertEqual(resultado["receita_total"], 175.35)
        self.assertIsInstance(resultado["receita_total"], float)
        self.assertEqual(resultado["ticket_medio"], 43.84)
        self.assertEqual(
            list(resultado["por_categoria"].items()),
            [("Casa", 75.25), ("Eletronicos", 100.1)],
        )
        self.assertEqual(
            resultado["top_clientes"],
            [
                {"cliente": "Ana", "total": 125.35},
                {"cliente": "Bruno", "total": 50.0},
                {"cliente": "Eva", "total": 0.0},
            ],
        )

        with open(saida, encoding="utf-8") as f:
            self.assertEqual(json.load(f), resultado)

    def test_status_customizado_e_empate_alfabetico(self):
        conteudo = (
            CABECALHO
            + "1,d,Zeta,A,10,pendente\n"
            + "2,d,Alfa,A,10,pendente\n"
            + "3,d,Beta,A,5,pendente\n"
        )
        caminho = self._csv(conteudo)
        resultado = processar_vendas(
            caminho, self._saida("o.json"), status_filtro="Pendente", top_n=2
        )
        self.assertEqual(
            resultado["top_clientes"],
            [{"cliente": "Alfa", "total": 10.0}, {"cliente": "Zeta", "total": 10.0}],
        )
        self.assertEqual(resultado["total_transacoes"], 3)

    def test_sem_transacoes_validas_ticket_zero(self):
        caminho = self._csv(CABECALHO + "1,d,Ana,A,10,cancelado\n")
        resultado = processar_vendas(caminho, self._saida("o.json"))
        self.assertEqual(resultado["total_transacoes"], 0)
        self.assertEqual(resultado["ticket_medio"], 0.0)
        self.assertEqual(resultado["top_clientes"], [])

    def test_saida_utf8_sem_escape_ascii(self):
        caminho = self._csv(CABECALHO + "1,d,José,Café,10,concluido\n")
        saida = self._saida("o.json")
        processar_vendas(caminho, saida)
        with open(saida, encoding="utf-8") as f:
            texto = f.read()
        self.assertIn("José", texto)
        self.assertIn("Café", texto)
        self.assertIn('\n  "total_transacoes"', texto)


if __name__ == "__main__":
    unittest.main()
