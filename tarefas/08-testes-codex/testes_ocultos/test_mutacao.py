"""Avaliação da suíte submetida em cópias independentes e sem rede."""
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import pytest

OCULTOS = Path(__file__).resolve().parent
TRABALHO = OCULTOS.parent
MUTANTES = sorted((OCULTOS / 'mutantes').glob('mutante_*.py'))


def executar_suite(modulo):
    testes = TRABALHO / 'tests'
    assert testes.is_dir(), 'Crie tests/test_*.py'
    assert any(testes.glob('test_*.py')), 'Nenhum arquivo tests/test_*.py encontrado'
    with tempfile.TemporaryDirectory(prefix='suite-carrinho-') as pasta:
        sandbox = Path(pasta)
        shutil.copytree(testes, sandbox / 'tests', ignore=shutil.ignore_patterns('__pycache__', '.pytest_cache'))
        shutil.copyfile(modulo, sandbox / 'carrinho.py')
        env = os.environ.copy()
        env['PYTHONPATH'] = str(sandbox)
        env['PYTEST_DISABLE_PLUGIN_AUTOLOAD'] = '1'
        env.pop('PYTEST_ADDOPTS', None)
        env.pop('PYTEST_PLUGINS', None)
        try:
            return subprocess.run([sys.executable, '-m', 'pytest', '-q', 'tests',
                                   '--tb=short', '-p', 'no:cacheprovider'],
                                  cwd=sandbox, env=env, capture_output=True, text=True, timeout=8)
        except subprocess.TimeoutExpired:
            pytest.fail('A suíte submetida excedeu 8 segundos por execução')


@pytest.fixture(scope='session')
def suite_valida():
    resultado = executar_suite(OCULTOS / 'suporte' / 'carrinho_correto.py')
    assert resultado.returncode == 0, ('A suíte deve passar no módulo correto.\n'
                                        + resultado.stdout + resultado.stderr)
    return resultado


def test_suite_passou_no_modulo_correto(suite_valida):
    assert suite_valida.returncode == 0


@pytest.mark.parametrize('mutante', MUTANTES, ids=lambda p: p.stem)
def test_mata_mutante(mutante, suite_valida):
    resultado = executar_suite(mutante)
    # Código 1 significa falha de teste; erro de coleta (2) ou ausência (5) não mata.
    assert resultado.returncode == 1, (f'{mutante.stem}: esperado teste falhar (código 1), '
                                      f'obtido {resultado.returncode}.\n'
                                      + resultado.stdout + resultado.stderr)
