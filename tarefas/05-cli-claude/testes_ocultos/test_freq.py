import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "freq.py"


def rodar(*args, entrada=None):
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING="utf-8")
    return subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        input=entrada, capture_output=True, text=True, encoding="utf-8", env=env, timeout=30,
    )


@pytest.fixture
def arquivo(tmp_path):
    def criar(conteudo, nome="t.txt"):
        caminho = tmp_path / nome
        caminho.write_text(conteudo, encoding="utf-8")
        return caminho
    return criar


def linhas(saida):
    return saida.splitlines()


def test_exemplo_do_enunciado(arquivo):
    r = rodar("-i", "-n", "2", arquivo("A casa, a CASA; a casa!\n"))
    assert r.returncode == 0
    assert linhas(r.stdout) == ["a\t3", "casa\t3"]
    assert r.stderr == ""


def test_padrao_diferencia_maiusculas_e_desempata(arquivo):
    r = rodar(arquivo("b a B a c b"))
    assert r.returncode == 0
    assert linhas(r.stdout) == ["a\t2", "b\t2", "B\t1", "c\t1"]


def test_top_padrao_10(arquivo):
    palavras = [f"p{chr(97 + i)}" for i in range(15)]  # pa..po, uma vez cada
    r = rodar(arquivo(" ".join(palavras)))
    assert r.returncode == 0
    assert linhas(r.stdout) == [f"{palavra}\t1" for palavra in palavras[:10]]
    assert r.stderr == ""


def test_flags_longas(arquivo):
    r = rodar("--top", "1", "--min-len", "4", "--ignore-case", arquivo("Sol sol SOL lua Lua mares Mares"))
    assert r.returncode == 0
    assert linhas(r.stdout) == ["mares\t2"]


def test_definicao_de_palavra_unicode(arquivo):
    r = rodar("-n", "20", arquivo("ação_ação x1y café-com-leite 42 ÁGUA"))
    assert r.returncode == 0
    esperado = sorted(["ação\t2", "x\t1", "y\t1", "café\t1", "com\t1", "leite\t1", "ÁGUA\t1"],
                      key=lambda s: (-int(s.split("\t")[1]), s.split("\t")[0]))
    assert linhas(r.stdout) == esperado


def test_formato_json(arquivo):
    r = rodar("--formato", "json", "-n", "2", arquivo("z z y x"))
    assert r.returncode == 0
    assert json.loads(r.stdout) == [{"palavra": "z", "contagem": 2}, {"palavra": "x", "contagem": 1}]


def test_sem_palavras(arquivo):
    caminho = arquivo("123 ... 456\n")
    r = rodar(caminho)
    assert r.returncode == 0 and r.stdout == ""
    r = rodar("--formato", "json", caminho)
    assert r.returncode == 0 and json.loads(r.stdout) == []


def test_stdin():
    r = rodar("-", "-i", entrada="Olá olá mundo\n")
    assert r.returncode == 0
    assert linhas(r.stdout) == ["olá\t2", "mundo\t1"]


def test_arquivo_inexistente(tmp_path):
    r = rodar(tmp_path / "nao_existe.txt")
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr.startswith("erro: ")
    assert len(r.stderr.strip().splitlines()) == 1


def test_diretorio(tmp_path):
    r = rodar(tmp_path)
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr.startswith("erro: ")
    assert len(r.stderr.strip().splitlines()) == 1


def test_utf8_invalido(tmp_path):
    caminho = tmp_path / "latin1.txt"
    caminho.write_bytes("ação".encode("latin-1"))
    r = rodar(caminho)
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr.startswith("erro: ")
    assert len(r.stderr.strip().splitlines()) == 1


@pytest.mark.parametrize(
    "args",
    [
        [],
        ["-n", "0", "ARQ"],
        ["-n", "-3", "ARQ"],
        ["-n", "abc", "ARQ"],
        ["-m", "0", "ARQ"],
        ["--formato", "xml", "ARQ"],
        ["--opcao-que-nao-existe", "ARQ"],
    ],
)
def test_argumentos_invalidos(arquivo, args):
    caminho = str(arquivo("a b c"))
    r = rodar(*[caminho if a == "ARQ" else a for a in args])
    assert r.returncode == 2
    assert r.stdout == ""
    assert "usage" in r.stderr.lower() or "uso" in r.stderr.lower()


def test_help(arquivo):
    r = rodar("--help")
    assert r.returncode == 0
    for opcao in ("--top", "--min-len", "--ignore-case", "--formato"):
        assert opcao in r.stdout
