from collections import Counter
import json
import os
from pathlib import Path
import subprocess
import sys
import pytest
from cli import main

ROOT = Path(__file__).resolve().parents[1]
ENV = {**os.environ, 'PYTHONIOENCODING': 'utf-8'}


def executar(caminho, *flags):
    return subprocess.run([sys.executable, str(ROOT / 'cli.py'), str(caminho), *flags],
                          cwd=ROOT, env=ENV, capture_output=True, text=True,
                          encoding='utf-8', timeout=10)


@pytest.mark.parametrize('json_flag', [False, True])
def test_top_depois_da_contagem_do_casefold_e_da_ordem(tmp_path, json_flag):
    caminho = tmp_path / 'entrada ação.txt'
    caminho.write_text('z z z z z b b b a a a Straße STRASSE straße', encoding='utf-8')
    flags = ['--top', '3', '--minimo', '3', '--ignorar-caixa']
    if json_flag:
        flags.append('--json')
    r = executar(caminho, *flags)
    assert r.returncode == 0 and r.stderr == ''
    if json_flag:
        assert json.loads(r.stdout) == [
            {'palavra': 'z', 'contagem': 5}, {'palavra': 'a', 'contagem': 3},
            {'palavra': 'b', 'contagem': 3}]
        assert r.stdout.endswith('\n') and len(r.stdout.splitlines()) == 1
    else:
        assert r.stdout == 'z\t5\na\t3\nb\t3\n'


def test_unicode_separadores_pontuacao_sem_normalizacao(tmp_path):
    caminho = tmp_path / 'unicode.txt'
    caminho.write_text('Σ ς σ\u00a0İ\u2003i\u0307\u2028é\fé\ve\u0301\r\n'
                       'a\u200bb a\u200bb !a !a', encoding='utf-8')
    r = executar(caminho, '--ignorar-caixa', '--json')
    assert r.returncode == 0 and r.stderr == ''
    assert json.loads(r.stdout) == [
        {'palavra': 'σ', 'contagem': 3}, {'palavra': '!a', 'contagem': 2},
        {'palavra': 'a\u200bb', 'contagem': 2}, {'palavra': 'i\u0307', 'contagem': 2},
        {'palavra': 'é', 'contagem': 2}, {'palavra': 'e\u0301', 'contagem': 1}]
    assert 'é' in r.stdout and 'σ' in r.stdout


@pytest.mark.parametrize('valor', ['0', '-1', '1.5', 'abc'])
def test_top_invalido(tmp_path, valor):
    caminho = tmp_path / 'ok.txt'
    caminho.write_text('ok', encoding='utf-8')
    r = executar(caminho, '--json', '--top', valor)
    assert r.returncode == 2 and r.stdout == ''
    assert r.stderr.strip() and 'Traceback' not in r.stderr


def test_volume_e_limite_maior_que_resultados(tmp_path):
    palavras = [f'p{i % 173:03d}' for i in range(100_000)]
    contagens = Counter(palavras)
    esperado = [{'palavra': palavra, 'contagem': n} for palavra, n in
                sorted(contagens.items(), key=lambda item: (-item[1], item[0]))]
    caminho = tmp_path / 'grande.txt'
    caminho.write_text('\t'.join(palavras), encoding='utf-8')
    r = executar(caminho, '--json', '--top', '1000000')
    assert r.returncode == 0 and r.stderr == ''
    assert json.loads(r.stdout) == esperado
    r = executar(caminho, '--json', '--top', '1', '--minimo', '999999')
    assert r.returncode == 0 and r.stderr == '' and r.stdout == '[]\n'


def test_importar_sem_efeitos():
    r = subprocess.run([sys.executable, '-c', 'import cli', '--inexistente'],
                       cwd=ROOT, env=ENV, capture_output=True, text=True,
                       encoding='utf-8', timeout=10)
    assert r.returncode == 0 and r.stdout == '' and r.stderr == ''


def test_main_repetido_e_argv_none(tmp_path, capsys, monkeypatch):
    caminho = tmp_path / 'repetido.txt'
    caminho.write_text('X x x y', encoding='utf-8')
    assert main([str(caminho), '--ignorar-caixa', '--top', '1']) == 0
    captura = capsys.readouterr()
    assert captura.out == 'x\t3\n' and captura.err == ''
    monkeypatch.setattr(sys, 'argv', ['cli.py', str(caminho), '--json'])
    assert main() == 0
    captura = capsys.readouterr()
    assert json.loads(captura.out) == [dict(palavra='x', contagem=2),
                                     dict(palavra='X', contagem=1), dict(palavra='y', contagem=1)]
    assert captura.err == ''
    caminho.write_text('', encoding='utf-8')
    assert main([str(caminho), '--top', '1']) == 0
    captura = capsys.readouterr()
    assert captura.out == '' and captura.err == ''
