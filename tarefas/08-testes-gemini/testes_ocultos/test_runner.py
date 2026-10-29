from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import pytest

ROOT_DIR = Path(__file__).resolve().parent.parent
MUTANTES_DIR = Path(__file__).resolve().parent / "mutantes"


def run_candidate_tests(workdir: Path):
    cmd = [sys.executable, "-m", "pytest", "-q", "tests"]
    try:
        return subprocess.run(cmd, cwd=str(workdir), capture_output=True, text=True, timeout=10)
    except subprocess.TimeoutExpired:
        pytest.fail("A suíte do candidato excedeu o limite de 10s; timeout não elimina mutantes.")


def executar_suite_isolada(modulo: Path):
    with tempfile.TemporaryDirectory() as temp_dir_str:
        temp_dir = Path(temp_dir_str)
        shutil.copyfile(modulo, temp_dir / "validador.py")
        shutil.copytree(
            ROOT_DIR / "tests", temp_dir / "tests",
            ignore=shutil.ignore_patterns("__pycache__", ".pytest_cache", "*.pyc"),
        )
        return run_candidate_tests(temp_dir)


def test_suite_passa_no_modulo_original():
    tests_dir = ROOT_DIR / "tests"
    assert tests_dir.is_dir(), "Diretório 'tests/' não encontrado no diretório raiz da solução."
    # Deixa o pytest descobrir também subpastas e arquivos *_test.py.
    # Original e mutantes recebem a mesma estrutura isolada de arquivos.
    res = executar_suite_isolada(ROOT_DIR / "validador.py")
    assert res.returncode == 0, (
        f"A suíte de testes do candidato falhou ao rodar contra o módulo original correto!\n"
        f"Stdout:\n{res.stdout}\nStderr:\n{res.stderr}"
    )


def executar_mutante(nome_mutante: str):
    mutante_file = MUTANTES_DIR / f"{nome_mutante}.py"
    assert mutante_file.is_file(), f"Arquivo do mutante não encontrado: {mutante_file}"

    res = executar_suite_isolada(mutante_file)
    # Código 1 indica falha de testes; erros de coleta, uso, ausência de testes
    # e interrupções não demonstram que a suíte detectou o bug do mutante.
    assert res.returncode == 1, (
        f"O mutante {nome_mutante} não foi eliminado por uma falha de teste "
        f"(código esperado 1, obtido {res.returncode}).\n"
        f"Stdout:\n{res.stdout}\nStderr:\n{res.stderr}"
    )


def test_mata_mutante_01():
    executar_mutante("mutante_01")


def test_mata_mutante_02():
    executar_mutante("mutante_02")


def test_mata_mutante_03():
    executar_mutante("mutante_03")


def test_mata_mutante_04():
    executar_mutante("mutante_04")


def test_mata_mutante_05():
    executar_mutante("mutante_05")


def test_mata_mutante_06():
    executar_mutante("mutante_06")


def test_mata_mutante_07():
    executar_mutante("mutante_07")


def test_mata_mutante_08():
    executar_mutante("mutante_08")


def test_mata_mutante_09():
    executar_mutante("mutante_09")


def test_mata_mutante_10():
    executar_mutante("mutante_10")
