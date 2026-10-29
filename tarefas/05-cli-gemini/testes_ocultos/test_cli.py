import json
import os
from pathlib import Path
import subprocess
import sys
import pytest

CLI_PATH = str(Path(__file__).resolve().parent.parent / "contatexto.py")


def run_cli(*args):
    cmd = [sys.executable, CLI_PATH, *args]
    ambiente = dict(os.environ, PYTHONIOENCODING="utf-8", PYTHONUTF8="1")
    return subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          env=ambiente, timeout=10)


@pytest.fixture
def arquivo_exemplo(tmp_path):
    p = tmp_path / "exemplo.txt"
    p.write_text("Ola mundo!\nPython e incrivel.\nMundo python.", encoding="utf-8")
    return str(p)


def test_padrao_sem_flags(arquivo_exemplo):
    res = run_cli(arquivo_exemplo)
    assert res.returncode == 0
    saida = res.stdout
    assert "Linhas: 3" in saida
    assert "Palavras: 7" in saida
    assert "Caracteres: 43" in saida
    assert "Top Palavras" not in saida


def test_flag_individual_linhas(arquivo_exemplo):
    res = run_cli(arquivo_exemplo, "--linhas")
    assert res.returncode == 0
    saida = res.stdout.strip()
    assert saida == "Linhas: 3"
    assert "Palavras" not in saida
    assert "Caracteres" not in saida


def test_flag_palavras_e_chars(arquivo_exemplo):
    res = run_cli(arquivo_exemplo, "-p", "-c")
    assert res.returncode == 0
    saida = res.stdout
    assert "Linhas" not in saida
    assert "Palavras: 7" in saida
    assert "Caracteres: 43" in saida


def test_flag_top_palavras(arquivo_exemplo):
    res = run_cli(arquivo_exemplo, "--top", "2")
    assert res.returncode == 0
    saida = res.stdout
    assert "Top Palavras:" in saida
    assert saida.splitlines() == ["Top Palavras:", "  - mundo: 2", "  - python: 2"]


def test_modo_json(arquivo_exemplo):
    res = run_cli(arquivo_exemplo, "--json", "-l", "--top", "1")
    assert res.returncode == 0
    dados = json.loads(res.stdout)
    assert dados == {
        "linhas": 3,
        "top_palavras": [{"palavra": "mundo", "ocorrencias": 2}],
    }


def test_flag_saida_arquivo(arquivo_exemplo, tmp_path):
    out_file = tmp_path / "saida.txt"
    res = run_cli(arquivo_exemplo, "-l", "-o", str(out_file))
    assert res.returncode == 0
    assert res.stdout == f"Salvo em {out_file}\n"
    assert out_file.is_file()
    assert out_file.read_text(encoding="utf-8").strip() == "Linhas: 3"


def test_flag_saida_cria_subdiretorios_inexistentes(arquivo_exemplo, tmp_path):
    out_file = tmp_path / "nivel1" / "nivel2" / "saida_aninhada.txt"
    res = run_cli(arquivo_exemplo, "-l", "-o", str(out_file))
    assert res.returncode == 0
    assert res.stdout == f"Salvo em {out_file}\n"
    assert out_file.is_file()
    assert out_file.read_text(encoding="utf-8").strip() == "Linhas: 3"


def test_arquivo_inexistente_exit_1(tmp_path):
    res = run_cli(str(tmp_path / "arquivo_fantasma.txt"))
    assert res.returncode == 1
    assert res.stderr.startswith("Erro")


def test_caminho_e_diretorio_exit_1(tmp_path):
    diretorio = tmp_path / "meu_diretorio"
    diretorio.mkdir()
    res = run_cli(str(diretorio))
    assert res.returncode == 1
    assert res.stderr.startswith("Erro")


def test_top_invalido_exit_2(arquivo_exemplo):
    res = run_cli(arquivo_exemplo, "--top", "0")
    assert res.returncode == 2


def test_sem_argumentos_exit_2():
    res = run_cli()
    assert res.returncode == 2


def test_arquivo_vazio(tmp_path):
    p = tmp_path / "vazio.txt"
    p.write_text("", encoding="utf-8")
    res = run_cli(str(p), "--json")
    assert res.returncode == 0
    dados = json.loads(res.stdout)
    assert dados["linhas"] == 0
    assert dados["palavras"] == 0
    assert dados["caracteres"] == 0


@pytest.mark.parametrize("flags", [("--inexistente",), ("--top", "-1"), ("--top", "abc"), ("--top",)])
def test_erros_de_sintaxe_exit_2(arquivo_exemplo, flags):
    assert run_cli(arquivo_exemplo, *flags).returncode == 2


def test_tokens_pontuacao_unicode_e_espacos(tmp_path):
    arquivo = tmp_path / "texto.txt"
    texto = 'Árvore!\t(árvore)  {BOLA}\n... bola; ""\n'
    arquivo.write_text(texto, encoding="utf-8")
    res = run_cli(str(arquivo), "-l", "-p", "--chars", "--top", "20", "--json")
    assert res.returncode == 0
    assert json.loads(res.stdout) == {
        "linhas": 2, "palavras": 6, "caracteres": len(texto),
        "top_palavras": [
            {"palavra": "bola", "ocorrencias": 2},
            {"palavra": "árvore", "ocorrencias": 2},
        ],
    }
    assert res.stdout.rstrip("\n") == json.dumps(json.loads(res.stdout), indent=2, ensure_ascii=False)


def test_top_sem_palavras(tmp_path):
    arquivo = tmp_path / "pontuacao.txt"
    arquivo.write_text("... () !!!", encoding="utf-8")
    res = run_cli(str(arquivo), "--json", "--top", "1")
    assert res.returncode == 0
    assert json.loads(res.stdout) == {"top_palavras": []}


def test_erro_de_leitura_utf8(tmp_path):
    arquivo = tmp_path / "invalido.txt"
    arquivo.write_bytes(b"\xff\xfe")
    res = run_cli(str(arquivo))
    assert res.returncode == 1
    assert res.stderr.startswith("Erro")


def test_json_gravado_em_arquivo(arquivo_exemplo, tmp_path):
    saida = tmp_path / "saida.json"
    res = run_cli(arquivo_exemplo, "--json", "-p", "--saida", str(saida))
    assert res.returncode == 0
    assert res.stdout == f"Salvo em {saida}\n"
    assert json.loads(saida.read_text(encoding="utf-8")) == {"palavras": 7}


def test_quebras_de_linha_crlf_e_lf_mistas(tmp_path):
    arquivo = tmp_path / "crlf.txt"
    arquivo.write_bytes(b"Linha 1\r\nLinha 2\nLinha 3\r\n")
    res = run_cli(str(arquivo), "--json", "-l", "-p")
    assert res.returncode == 0
    dados = json.loads(res.stdout)
    assert dados["linhas"] == 3
    assert dados["palavras"] == 6


def test_pontuacoes_aninhadas_e_aspas_multiplas(tmp_path):
    arquivo = tmp_path / "aninhado.txt"
    arquivo.write_text('"""[[[palavra]]]""" ...palavra... ((palavra))!?', encoding="utf-8")
    res = run_cli(str(arquivo), "--json", "--top", "1")
    assert res.returncode == 0
    dados = json.loads(res.stdout)
    assert dados["top_palavras"] == [{"palavra": "palavra", "ocorrencias": 3}]
