"""Testes da interface pública da CLI, executados com unittest."""

import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


RAIZ = Path(__file__).resolve().parent


class ContatextoTests(unittest.TestCase):
    def setUp(self):
        self.temporario = tempfile.TemporaryDirectory(dir=RAIZ)
        self.addCleanup(self.temporario.cleanup)
        self.pasta = Path(self.temporario.name)
        self.entrada = self.pasta / "entrada.txt"
        self.entrada.write_text('Olá, mundo!\nOlá python.\n', encoding="utf-8")

    def executar(self, *argumentos):
        return subprocess.run(
            [sys.executable, str(RAIZ / "contatexto.py"), *map(str, argumentos)],
            capture_output=True, text=True, encoding="utf-8", cwd=RAIZ,
        )

    def test_padrao(self):
        retorno = self.executar(self.entrada)
        self.assertEqual(retorno.returncode, 0, retorno.stderr)
        self.assertEqual(retorno.stdout, "Linhas: 2\nPalavras: 4\nCaracteres: 24\n")

    def test_selecao_de_metricas(self):
        for flag, chave, valor in [("-l", "linhas", 2), ("-p", "palavras", 4), ("-c", "caracteres", 24)]:
            with self.subTest(flag=flag):
                retorno = self.executar(self.entrada, flag, "--json")
                self.assertEqual(retorno.returncode, 0, retorno.stderr)
                self.assertEqual(json.loads(retorno.stdout), {chave: valor})

    def test_top_normalizacao_e_desempate(self):
        self.entrada.write_text('B! a, b A (ação) "ação" ... [] {}', encoding="utf-8")
        retorno = self.executar(self.entrada, "--top", 3, "--json")
        esperado = {"top_palavras": [
            {"palavra": "a", "ocorrencias": 2},
            {"palavra": "ação", "ocorrencias": 2},
            {"palavra": "b", "ocorrencias": 2},
        ]}
        self.assertEqual(json.loads(retorno.stdout), esperado)
        self.assertEqual(retorno.stdout, json.dumps(esperado, indent=2, ensure_ascii=False) + "\n")

    def test_top_texto_com_metrica(self):
        retorno = self.executar(self.entrada, "--palavras", "--top", 2)
        self.assertEqual(retorno.stdout, "Palavras: 4\nTop Palavras:\n  - olá: 2\n  - mundo: 1\n")

    def test_arquivo_vazio(self):
        self.entrada.write_bytes(b"")
        retorno = self.executar(self.entrada, "--json")
        self.assertEqual(json.loads(retorno.stdout), {"linhas": 0, "palavras": 0, "caracteres": 0})
        retorno = self.executar(self.entrada, "--top", 10, "--json")
        self.assertEqual(json.loads(retorno.stdout), {"top_palavras": []})

    def test_quebras_de_linha_e_unicode(self):
        conteudo = "á\r\nb\rc\u2028d"
        self.entrada.write_bytes(conteudo.encode("utf-8"))
        retorno = self.executar(self.entrada, "--json")
        self.assertEqual(json.loads(retorno.stdout), {"linhas": 4, "palavras": 4, "caracteres": len(conteudo)})

    def test_saida_cria_pastas(self):
        destino = self.pasta / "nova" / "subpasta" / "resultado.json"
        retorno = self.executar(self.entrada, "-l", "--json", "--saida", destino)
        self.assertEqual(retorno.returncode, 0, retorno.stderr)
        self.assertEqual(retorno.stdout, f"Salvo em {destino}\n")
        self.assertEqual(destino.read_text(encoding="utf-8"), '{\n  "linhas": 2\n}\n')

    def test_erros_operacionais(self):
        invalido = self.pasta / "invalido.txt"
        invalido.write_bytes(b"\xff")
        for caminho in (self.pasta / "ausente", self.pasta, invalido):
            with self.subTest(caminho=caminho):
                retorno = self.executar(caminho)
                self.assertEqual(retorno.returncode, 1)
                self.assertTrue(retorno.stderr.startswith("Erro"))
                self.assertEqual(retorno.stdout, "")
        retorno = self.executar(self.entrada, "-o", self.pasta)
        self.assertEqual(retorno.returncode, 1)
        self.assertTrue(retorno.stderr.startswith("Erro"))

    def test_erros_de_argumentos(self):
        for argumentos in ((), (self.entrada, "--inexistente"), (self.entrada, "--top", "0"), (self.entrada, "--top", "-1"), (self.entrada, "--top", "abc")):
            with self.subTest(argumentos=argumentos):
                retorno = self.executar(*argumentos)
                self.assertEqual(retorno.returncode, 2)
                self.assertEqual(retorno.stdout, "")


if __name__ == "__main__":
    unittest.main()
