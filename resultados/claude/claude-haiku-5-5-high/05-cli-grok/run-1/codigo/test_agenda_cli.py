import json
import os
import subprocess
import sys
import tempfile
import unittest

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "agenda_cli.py")


class AgendaCliTest(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.TemporaryDirectory()
        self.arquivo = os.path.join(self.dir.name, "agenda.json")

    def tearDown(self):
        self.dir.cleanup()

    def rodar(self, *args):
        return subprocess.run(
            [sys.executable, SCRIPT, *args],
            capture_output=True,
            timeout=30,
        )

    def escrever_json(self, dados):
        with open(self.arquivo, "w", encoding="utf-8") as f:
            json.dump(dados, f, ensure_ascii=False)

    def ler_json(self):
        with open(self.arquivo, encoding="utf-8") as f:
            return json.load(f)

    def adicionar(self, titulo, prioridade="media", *extra):
        return self.rodar("adicionar", "--titulo", titulo, "--prioridade", prioridade,
                          *extra, "--arquivo", self.arquivo)

    def assertErro(self, resultado, mensagem):
        self.assertEqual(resultado.returncode, 2)
        self.assertEqual(resultado.stdout, b"")
        self.assertEqual(resultado.stderr, f"erro: {mensagem}\n".encode())

    # --- argparse ---

    def test_sem_subcomando(self):
        r = self.rodar()
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stdout, b"")

    def test_argumento_desconhecido(self):
        r = self.rodar("listar", "--arquivo", self.arquivo, "--nada")
        self.assertEqual(r.returncode, 2)

    def test_prioridade_invalida(self):
        r = self.adicionar("x", "urgente")
        self.assertEqual(r.returncode, 2)
        self.assertEqual(r.stdout, b"")

    def test_arquivo_obrigatorio(self):
        r = self.rodar("listar")
        self.assertEqual(r.returncode, 2)

    # --- adicionar ---

    def test_adicionar_cria_arquivo(self):
        r = self.adicionar("  Comprar leite  ", "alta", "--prazo", "2000-02-29")
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, b"ok id=1\n", b""))
        self.assertEqual(self.ler_json(), {
            "proximo_id": 2,
            "tarefas": [{"id": 1, "titulo": "Comprar leite", "prioridade": "alta",
                         "prazo": "2000-02-29", "concluida": False}],
        })

    def test_adicionar_formato_do_arquivo(self):
        self.adicionar("Açúcar")
        with open(self.arquivo, "rb") as f:
            bruto = f.read()
        self.assertTrue(bruto.endswith(b"\n"))
        self.assertIn("Açúcar".encode("utf-8"), bruto)
        self.assertEqual(bruto.decode("utf-8"), json.dumps(self.ler_json(), indent=2, ensure_ascii=False) + "\n")

    def test_titulo_vazio(self):
        self.assertErro(self.adicionar("    "), "titulo vazio")
        self.assertFalse(os.path.exists(self.arquivo))

    def test_titulo_com_tab_ou_quebra(self):
        self.assertErro(self.adicionar("a\tb"), "titulo invalido")
        self.assertErro(self.adicionar("a\nb"), "titulo invalido")
        self.assertErro(self.adicionar("a\rb"), "titulo invalido")

    def test_prazo_invalido(self):
        for prazo in ["1900-02-29", "2100-02-29", "2024-13-01", "2024-1-01", "", "20240101"]:
            self.assertErro(self.adicionar("x", "media", "--prazo", prazo), "prazo invalido")

    def test_ids_com_buracos(self):
        self.escrever_json({"proximo_id": 5, "tarefas": [
            {"id": 1, "titulo": "a", "prioridade": "baixa", "prazo": None, "concluida": False},
            {"id": 3, "titulo": "b", "prioridade": "baixa", "prazo": None, "concluida": False},
        ]})
        r = self.adicionar("c")
        self.assertEqual(r.stdout, b"ok id=5\n")
        self.assertEqual(self.ler_json()["proximo_id"], 6)

    def test_arquivo_invalido_permanece_intacto(self):
        original = b'{"proximo_id": 1, "tarefas": [], "extra": 1}'
        with open(self.arquivo, "wb") as f:
            f.write(original)
        self.assertErro(self.adicionar("x"), "arquivo invalido")
        with open(self.arquivo, "rb") as f:
            self.assertEqual(f.read(), original)

    # --- listar ---

    def test_listar_ordem_e_colunas(self):
        self.adicionar("baixa-1", "baixa")
        self.adicionar("alta-2", "alta", "--prazo", "2030-01-02")
        self.adicionar("media-3", "media")
        self.adicionar("alta-4", "alta")
        self.rodar("concluir", "--id", "4", "--arquivo", self.arquivo)
        r = self.rodar("listar", "--arquivo", self.arquivo)
        self.assertEqual(r.returncode, 0)
        self.assertEqual(r.stdout.decode(), (
            "2\talta\taberta\t2030-01-02\talta-2\n"
            "4\talta\tconcluida\t-\talta-4\n"
            "3\tmedia\taberta\t-\tmedia-3\n"
            "1\tbaixa\taberta\t-\tbaixa-1\n"
        ))

    def test_listar_filtros_combinados(self):
        self.adicionar("a", "alta")
        self.adicionar("b", "alta")
        self.adicionar("c", "baixa")
        self.rodar("concluir", "--id", "1", "--arquivo", self.arquivo)
        r = self.rodar("listar", "--arquivo", self.arquivo, "--prioridade", "alta", "--somente-abertas")
        self.assertEqual(r.stdout.decode(), "2\talta\taberta\t-\tb\n")

    def test_listar_vazio(self):
        self.adicionar("a", "alta")
        self.rodar("concluir", "--id", "1", "--arquivo", self.arquivo)
        r = self.rodar("listar", "--arquivo", self.arquivo, "--somente-abertas")
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, b"", b""))

    def test_listar_nao_reescreve(self):
        self.adicionar("a")
        with open(self.arquivo, "rb") as f:
            antes = f.read()
        self.rodar("listar", "--arquivo", self.arquivo)
        with open(self.arquivo, "rb") as f:
            self.assertEqual(f.read(), antes)

    def test_arquivo_inexistente(self):
        for sub in (["listar"], ["concluir", "--id", "1"]):
            self.assertErro(self.rodar(*sub, "--arquivo", self.arquivo), "arquivo inexistente")

    def test_arquivo_invalido_na_leitura(self):
        invalidos = [
            "[]",
            '{"proximo_id": 1.0, "tarefas": []}',
            '{"proximo_id": true, "tarefas": []}',
            '{"proximo_id": 1, "tarefas": [], "tarefas": []}',
            '{"proximo_id": 2, "tarefas": [{"id": 1, "titulo": " a", "prioridade": "alta", "prazo": null, "concluida": false}]}',
            '{"proximo_id": 1, "tarefas": [{"id": 1, "titulo": "a", "prioridade": "alta", "prazo": null, "concluida": false}]}',
            '{"proximo_id": 3, "tarefas": [{"id": 1, "titulo": "a", "prioridade": "alta", "prazo": "1900-02-29", "concluida": false}]}',
            '{"proximo_id": 3, "tarefas": [{"id": 1, "titulo": "a", "prioridade": "alta", "prazo": null, "concluida": 0}]}',
            '{"proximo_id": 3, "tarefas": [{"id": 1, "titulo": "a", "prioridade": "alta", "prazo": null, "concluida": false},'
            ' {"id": 1, "titulo": "b", "prioridade": "alta", "prazo": null, "concluida": false}]}',
        ]
        for texto in invalidos:
            with self.subTest(texto=texto):
                with open(self.arquivo, "w", encoding="utf-8") as f:
                    f.write(texto)
                self.assertErro(self.rodar("listar", "--arquivo", self.arquivo), "arquivo invalido")

    # --- concluir ---

    def test_concluir(self):
        self.adicionar("a")
        r = self.rodar("concluir", "--id", "01", "--arquivo", self.arquivo)
        self.assertEqual((r.returncode, r.stdout, r.stderr), (0, b"ok id=1\n", b""))
        self.assertTrue(self.ler_json()["tarefas"][0]["concluida"])

    def test_concluir_erros(self):
        self.adicionar("a")
        self.assertErro(self.rodar("concluir", "--id", "9", "--arquivo", self.arquivo), "id inexistente")
        self.rodar("concluir", "--id", "1", "--arquivo", self.arquivo)
        self.assertErro(self.rodar("concluir", "--id", "1", "--arquivo", self.arquivo), "ja concluida")


if __name__ == "__main__":
    unittest.main()
