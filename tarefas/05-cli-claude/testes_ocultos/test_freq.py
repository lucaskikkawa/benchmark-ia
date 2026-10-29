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


def rodar_bytes(*args, entrada: bytes, codificacao_terminal="utf-8"):
    # codificacao_terminal simula um terminal configurado com outra codificação.
    env = dict(os.environ, PYTHONUTF8="1", PYTHONIOENCODING=codificacao_terminal)
    r = subprocess.run(
        [sys.executable, str(SCRIPT), *map(str, args)],
        input=entrada, capture_output=True, env=env, timeout=30,
    )
    return r.returncode, r.stdout.decode("utf-8", "replace"), r.stderr.decode("utf-8", "replace")


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


def test_padrao_diferencia_maiusculas_e_desempata(arquivo):
    r = rodar(arquivo("b a B a c b"))
    assert r.returncode == 0
    assert linhas(r.stdout) == ["a\t2", "b\t2", "B\t1", "c\t1"]


def test_top_padrao_10(arquivo):
    palavras = [f"p{chr(97 + i)}" for i in range(15)]  # pa..po, uma vez cada
    r = rodar(arquivo(" ".join(palavras)))
    assert r.returncode == 0
    assert linhas(r.stdout) == [f"{palavra}\t1" for palavra in palavras[:10]]


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


def test_argumentos_invalidos(arquivo):
    caminho = str(arquivo("a b c"))
    casos = [
        [],
        ["-n", "0", "ARQ"],
        ["-n", "-3", "ARQ"],
        ["-n", "abc", "ARQ"],
        ["-m", "0", "ARQ"],
        ["--formato", "xml", "ARQ"],
        ["--opcao-que-nao-existe", "ARQ"],
        ["-x"],
    ]
    for args in casos:
        r = rodar(*[caminho if a == "ARQ" else a for a in args])
        assert r.returncode == 2, args
        assert r.stdout == "", args
        assert "usage" in r.stderr.lower() or "uso" in r.stderr.lower(), args


def test_help(arquivo):
    r = rodar("--help")
    assert r.returncode == 0
    for opcao in ("--top", "--min-len", "--ignore-case", "--excluir", "--formato"):
        assert opcao in r.stdout


# ---- requisitos adicionais ----

def test_excluir_exato_sem_ignore_case(arquivo):
    r = rodar("-x", "a", "--excluir", "casa", arquivo("A casa, a CASA; a casa! o o"))
    assert r.returncode == 0
    assert linhas(r.stdout) == ["o\t2", "A\t1", "CASA\t1"]


def test_excluir_com_ignore_case(arquivo):
    r = rodar("-i", "-x", "CASA", "-x", "o", arquivo("A casa, a CASA; a casa! o O ó"))
    assert r.returncode == 0
    assert linhas(r.stdout) == ["a\t3", "ó\t1"]


def test_excluir_combinado_com_min_len_e_json(arquivo):
    r = rodar("--formato", "json", "-m", "3", "-x", "sol", "-i", arquivo("Sol sol lua LUA lua mar de"))
    assert r.returncode == 0
    assert json.loads(r.stdout) == [{"palavra": "lua", "contagem": 3}, {"palavra": "mar", "contagem": 1}]


def test_ignore_case_usa_lower_e_nao_casefold(arquivo):
    r = rodar("-i", arquivo("Straße STRASSE strasse ǅemal ǆemal"))
    assert r.returncode == 0
    assert linhas(r.stdout) == ["strasse\t2", "ǆemal\t2", "straße\t1"]


def test_ignore_case_aplicado_depois_da_extracao(arquivo):
    # "İ".lower() == "i\u0307" (o ponto combinante não é letra): a palavra é extraída antes.
    r = rodar("-i", arquivo("İSTANBUL istanbul"))
    assert r.returncode == 0
    assert linhas(r.stdout) == ["istanbul\t1", "i\u0307stanbul\t1"]


def test_sem_normalizacao_unicode(arquivo):
    # "e" + acento combinante (NFD): o acento não é letra e separa palavras.
    r = rodar(arquivo("cafe\u0301 café cafe"))
    assert r.returncode == 0
    assert linhas(r.stdout) == ["cafe\t2", "café\t1"]


def test_digitos_unicode_separam_palavras(arquivo):
    r = rodar(arquivo("ab\u0663cd ab\uff15ab x\u0967y"))
    assert r.returncode == 0
    assert linhas(r.stdout) == ["ab\t3", "cd\t1", "x\t1", "y\t1"]


def test_stdin_utf8_invalido():
    codigo, saida, erro = rodar_bytes("-", entrada="ação ok".encode("latin-1"))
    assert codigo == 1
    assert saida == ""
    assert erro.startswith("erro: ")
    assert len(erro.strip().splitlines()) == 1


def test_stdin_utf8_invalido_independe_do_terminal():
    # Mesmo com o terminal em latin-1 (que decodifica qualquer byte), a entrada é UTF-8 estrito.
    codigo, saida, erro = rodar_bytes("-", entrada=b"ok \xff\xfe ok", codificacao_terminal="latin-1")
    assert codigo == 1
    assert saida == ""
    assert erro.startswith("erro: ")


def test_stdin_decodificado_como_utf8_independe_do_terminal():
    codigo, saida, _ = rodar_bytes(
        "-x", "aé", "-", entrada="aé aé b\n".encode("utf-8"), codificacao_terminal="latin-1"
    )
    assert codigo == 0
    assert linhas(saida) == ["b\t1"]


def test_stdin_bytes_utf8_validos():
    codigo, saida, _ = rodar_bytes("-i", "-", entrada="Ação ação AÇÃO\n".encode("utf-8"))
    assert codigo == 0
    assert linhas(saida) == ["ação\t3"]


def test_utf8_invalido_no_meio_de_arquivo_grande(tmp_path):
    caminho = tmp_path / "grande.txt"
    caminho.write_bytes(("palavra " * 200_000).encode("utf-8") + b"\xff" + b" fim")
    r = rodar(caminho)
    assert r.returncode == 1
    assert r.stdout == ""
    assert r.stderr.startswith("erro: ")


def test_arquivo_grande(arquivo):
    partes = []
    for i in range(300_000):
        partes.append(("alfa", "Beta", "gama", "beta", "delta")[i % 5] + ("," if i % 3 else "\n"))
    r = rodar("-i", "-n", "3", arquivo("".join(partes)))
    assert r.returncode == 0
    assert linhas(r.stdout) == ["beta\t120000", "alfa\t60000", "delta\t60000"]


def test_top_maior_que_numero_de_palavras_e_arquivo_vazio(arquivo):
    r = rodar("-n", "1000", arquivo("b a"))
    assert linhas(r.stdout) == ["a\t1", "b\t1"]
    r = rodar(arquivo(""))
    assert r.returncode == 0 and r.stdout == ""
