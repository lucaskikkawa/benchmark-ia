import json
import os
import tempfile
import unittest

from solucao import consolidar

CAB = "id,equipe,aberto_em,fechado_em,prioridade\n"
SLA = {"limites_minutos": {"baixa": 480, "media": 240, "alta": 60}}


class TestConsolidar(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = self._tmp.name
        self.csv = os.path.join(self.dir, "chamados.csv")
        self.sla = os.path.join(self.dir, "sla.json")
        self.saida = os.path.join(self.dir, "saida.json")
        self.escrever_sla(json.dumps(SLA))

    def tearDown(self):
        self._tmp.cleanup()

    def escrever_csv(self, texto):
        with open(self.csv, "w", encoding="utf-8", newline="") as f:
            f.write(texto)

    def escrever_sla(self, texto):
        with open(self.sla, "w", encoding="utf-8") as f:
            f.write(texto)

    def rodar(self, texto):
        self.escrever_csv(texto)
        return consolidar(self.csv, self.sla, self.saida)

    def assertErro(self, texto):
        with self.assertRaises(ValueError):
            self.rodar(texto)

    def test_exemplo(self):
        r = self.rodar(
            CAB
            + "a1,n1,2024-03-01T10:00,2024-03-01T11:01,alta\r\n"
            + "b2,n1,2024-03-01T10:00,2024-03-01T10:30,alta\n"
        )
        esperado = {
            "equipes": [
                {
                    "equipe": "n1",
                    "chamados": 2,
                    "estourados": 1,
                    "tempo_medio_minutos": 45,
                    "pior_id": "a1",
                }
            ]
        }
        self.assertEqual(r, esperado)
        with open(self.saida, encoding="utf-8", newline="") as f:
            self.assertEqual(f.read(), json.dumps(esperado, ensure_ascii=False, indent=2) + "\n")

    def test_empate_e_ordem(self):
        r = self.rodar(
            CAB
            + "a2,alfa,2024-03-01T10:00,2024-03-01T10:10,baixa\n"
            + "a10,alfa,2024-03-01T10:00,2024-03-01T10:10,baixa\n"
            + "x,\"São, Paulo\",2024-12-31T23:00,2025-01-01T01:00,media\n"
            + "y, A ,2024-03-01T10:00,2024-03-01T10:00, alta \n"
            + ",,,,\n\n   \n"
        )
        nomes = [e["equipe"] for e in r["equipes"]]
        self.assertEqual(nomes, ["A", "São, Paulo", "alfa"])
        self.assertEqual(r["equipes"][2]["pior_id"], "a10")
        self.assertEqual(r["equipes"][1]["tempo_medio_minutos"], 120)
        with open(self.saida, encoding="utf-8") as f:
            self.assertIn("São", f.read())

    def test_limite_igual_nao_estoura(self):
        r = self.rodar(CAB + "a,n,2024-03-01T10:00,2024-03-01T11:00,alta\n")
        self.assertEqual(r["equipes"][0]["estourados"], 0)

    def test_so_cabecalho(self):
        self.assertEqual(self.rodar(CAB + "\n\n"), {"equipes": []})

    def test_erros_csv(self):
        linha = "a,n,2024-03-01T10:00,2024-03-01T11:00,alta\n"
        self.assertErro("")
        self.assertErro("﻿" + CAB)
        self.assertErro("id,equipe,aberto_em,fechado_em,prioridade ,\n")
        self.assertErro(" id,equipe,aberto_em,fechado_em,prioridade\n")
        self.assertErro(CAB + "a,n,2024-03-01T10:00\n")
        self.assertErro(CAB + linha + " a ,m,2024-03-01T10:00,2024-03-01T11:00,alta\n")
        self.assertErro(CAB + ",n,2024-03-01T10:00,2024-03-01T11:00,alta\n")
        self.assertErro(CAB + "a, ,2024-03-01T10:00,2024-03-01T11:00,alta\n")
        self.assertErro(CAB + "a,n,2024-02-30T10:00,2024-03-01T11:00,alta\n")
        self.assertErro(CAB + "a,n,2024-3-01T10:00,2024-03-01T11:00,alta\n")
        self.assertErro(CAB + "a,n,2024-03-01 10:00,2024-03-01T11:00,alta\n")
        self.assertErro(CAB + "a,n,2024-03-01T10:00:00,2024-03-01T11:00,alta\n")
        self.assertErro(CAB + "a,n,2024-03-01T11:00,2024-03-01T10:59,alta\n")
        self.assertErro(CAB + "a,n,2024-03-01T10:00,2024-03-01T11:00,Alta\n")

    def test_erros_sla(self):
        linha = CAB + "a,n,2024-03-01T10:00,2024-03-01T11:00,alta\n"
        invalidos = [
            "",
            "{",
            "[]",
            '{"limites_minutos": {"baixa": 1, "media": 1}}',
            '{"limites_minutos": {"baixa": 1, "media": 1, "alta": 1}, "x": 1}',
            '{"limites_minutos": {"baixa": 1, "media": 1, "alta": true}}',
            '{"limites_minutos": {"baixa": 1, "media": 1, "alta": 1.0}}',
            '{"limites_minutos": {"baixa": 1, "media": 1, "alta": 0}}',
        ]
        for texto in invalidos:
            with self.subTest(texto=texto):
                self.escrever_sla(texto)
                self.assertErro(linha)

    def test_arquivo_ausente(self):
        with self.assertRaises(FileNotFoundError):
            consolidar(os.path.join(self.dir, "nao.csv"), self.sla, self.saida)
        self.escrever_csv(CAB)
        with self.assertRaises(FileNotFoundError):
            consolidar(self.csv, os.path.join(self.dir, "nao.json"), self.saida)


if __name__ == "__main__":
    unittest.main()
