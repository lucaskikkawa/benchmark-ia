"""Avalia a suíte tests/ escrita pelo modelo via mutation testing.

(a) a suíte deve passar contra o senhas.py correto;
(b) cada mutante (cópia de senhas.py com 1 bug) é um teste que passa
    se a suíte do modelo FALHAR nele (mutante morto).
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

AQUI = Path(__file__).resolve().parent
DIR_TRABALHO = AQUI.parent
MODULO_CORRETO = DIR_TRABALHO / "senhas.py"
TESTES_MODELO = DIR_TRABALHO / "tests"
MUTANTES = sorted((AQUI / "mutantes").glob("m*.py"))
TIMEOUT_S = 60


def rodar_suite(modulo: Path, destino: Path) -> subprocess.CompletedProcess:
    """Copia a suíte do modelo e `modulo` (como senhas.py) para `destino` e roda pytest."""
    shutil.copytree(TESTES_MODELO, destino / "tests", ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache"))
    shutil.copy(modulo, destino / "senhas.py")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    env.pop("PYTHONPATH", None)
    try:
        return subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-x", "-p", "no:cacheprovider", "tests"],
            cwd=destino, capture_output=True, text=True, timeout=TIMEOUT_S, env=env,
        )
    except subprocess.TimeoutExpired:
        return subprocess.CompletedProcess(args=[], returncode=-1, stdout="", stderr="timeout")


@pytest.fixture(scope="module")
def resultado_original(tmp_path_factory):
    if not TESTES_MODELO.is_dir() or not list(TESTES_MODELO.glob("test_*.py")):
        return None
    return rodar_suite(MODULO_CORRETO, tmp_path_factory.mktemp("original"))


def test_existe_suite_do_modelo():
    assert TESTES_MODELO.is_dir(), "diretório tests/ não encontrado"
    assert list(TESTES_MODELO.glob("test_*.py")), "nenhum tests/test_*.py encontrado"


def test_suite_passa_no_modulo_correto(resultado_original):
    assert resultado_original is not None, "suíte do modelo ausente"
    assert resultado_original.returncode == 0, resultado_original.stdout[-2000:] + resultado_original.stderr[-2000:]


def test_quantidade_de_mutantes():
    assert len(MUTANTES) >= 10


@pytest.mark.parametrize("mutante", MUTANTES, ids=[m.stem for m in MUTANTES])
def test_mutante_morto(mutante, resultado_original, tmp_path):
    # Só conta como morto se a suíte é válida (passa no módulo correto).
    if resultado_original is None or resultado_original.returncode != 0:
        pytest.fail("suíte do modelo não passa no módulo correto; mutante não pode ser considerado morto")
    resultado = rodar_suite(mutante, tmp_path)
    # 1 = algum teste falhou. 0 = mutante sobreviveu; 5 = nenhum teste coletado; -1 = timeout.
    assert resultado.returncode == 1, f"mutante sobreviveu (returncode={resultado.returncode})"
