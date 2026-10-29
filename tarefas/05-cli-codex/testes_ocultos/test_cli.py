import json
import os
from pathlib import Path
import subprocess
import sys
import pytest

ROOT = Path(__file__).resolve().parents[1]


def rodar(*args):
    # Fixa a codificação de stdio do processo filho: o resultado não pode depender do locale.
    env = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}
    return subprocess.run([sys.executable, str(ROOT / 'cli.py'), *map(str, args)],
                          cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8',
                          timeout=5)


def arquivo(tmp_path, conteudo):
    caminho = tmp_path / 'palavras com espaço.txt'
    caminho.write_text(conteudo, encoding='utf-8')
    return caminho


def sucesso(resultado):
    assert resultado.returncode == 0, resultado.stderr
    assert resultado.stderr == ''


def test_ordem_e_pontuacao(tmp_path):
    r = rodar(arquivo(tmp_path, 'b a b a c!\tc!\nz'))
    sucesso(r)
    assert r.stdout == 'a\t2\nb\t2\nc!\t2\nz\t1\n'


def test_case_sensitive_padrao(tmp_path):
    r = rodar(arquivo(tmp_path, 'A a A'))
    sucesso(r)
    assert r.stdout == 'A\t2\na\t1\n'


def test_casefold_unicode(tmp_path):
    r = rodar(arquivo(tmp_path, 'Straße STRASSE Á á'), '--ignorar-caixa')
    sucesso(r)
    assert r.stdout == 'strasse\t2\ná\t2\n'


def test_minimo_inclusivo(tmp_path):
    r = rodar(arquivo(tmp_path, 'b a b c c c'), '--minimo', '2')
    sucesso(r)
    assert r.stdout == 'c\t3\nb\t2\n'


def test_json_combinado(tmp_path):
    r = rodar('--json', '--minimo', '2', arquivo(tmp_path, 'Chá chá pão'), '--ignorar-caixa')
    sucesso(r)
    assert json.loads(r.stdout) == [{'palavra': 'chá', 'contagem': 2}]
    assert 'chá' in r.stdout
    assert len(r.stdout.splitlines()) == 1
    assert r.stdout.endswith('\n')


def test_vazio_texto(tmp_path):
    r = rodar(arquivo(tmp_path, ' \t\n'))
    sucesso(r)
    assert r.stdout == ''


def test_filtro_esvazia_json(tmp_path):
    r = rodar(arquivo(tmp_path, 'um'), '--json', '--minimo', '3')
    sucesso(r)
    assert r.stdout == '[]\n'


def test_help():
    r = rodar('--help')
    sucesso(r)
    assert '--minimo' in r.stdout and '--json' in r.stdout


@pytest.mark.parametrize('args', [[], ['--inexistente'], ['--minimo', '0'],
                                   ['--minimo', '-2'], ['--minimo', 'abc'], ['--minimo', '1.5']])
def test_erros_argumentos(tmp_path, args):
    # Para os casos de mínimo/flag, forneça arquivo válido para não mascarar o erro.
    completos = [] if not args else [arquivo(tmp_path, 'a'), *args]
    r = rodar(*completos)
    assert r.returncode == 2
    assert r.stdout == ''
    assert r.stderr.strip() and 'Traceback' not in r.stderr


def test_arquivo_ausente(tmp_path):
    r = rodar(tmp_path / 'nao-existe')
    assert r.returncode == 2 and r.stdout == ''
    assert r.stderr.strip() and 'Traceback' not in r.stderr


def test_utf8_invalido(tmp_path):
    p = tmp_path / 'ruim.txt'
    p.write_bytes(b'\xff')
    r = rodar(p)
    assert r.returncode == 2 and r.stdout == ''
    assert r.stderr.strip() and 'Traceback' not in r.stderr


def test_diretorio_como_arquivo(tmp_path):
    r = rodar(tmp_path)
    assert r.returncode == 2 and r.stdout == ''
    assert r.stderr.strip() and 'Traceback' not in r.stderr


def test_main_programatico(tmp_path, capsys):
    from cli import main
    assert main([str(arquivo(tmp_path, 'x x')), '--minimo', '2']) == 0
    capturado = capsys.readouterr()
    assert capturado.out == 'x\t2\n' and capturado.err == ''
