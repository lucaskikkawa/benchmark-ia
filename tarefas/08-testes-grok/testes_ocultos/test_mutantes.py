"""Roda a suíte do modelo no módulo correto e em cada mutante."""

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

RAIZ = Path(__file__).resolve().parents[1]
MODULO_CORRETO = RAIZ / "descontos.py"
DIR_TESTES = RAIZ / "tests"
DIR_MUTANTES = Path(__file__).resolve().parent / "mutantes"

MUTANTES = [
    "m01_off10.py",
    "m02_off5.py",
    "m03_fixo_sem_piso.py",
    "m04_bemvindo_fim.py",
    "m05_bemvindo_inicio.py",
    "m06_natal_dia24.py",
    "m07_cupom_desconhecido.py",
    "m08_cupom_vazio.py",
    "m09_cupom_fora_da_janela.py",
    "m10_preco_negativo.py",
    "m11_natal_por_subtracao.py",
    "m12_espacos_viram_vazio.py",
    "m13_1900_bissexto.py",
    "m14_rejeita_ano_1.py",
]


def _executar(origem_modulo: Path) -> tuple[int, str]:
    if not DIR_TESTES.is_dir() or not any(DIR_TESTES.glob("test_*.py")):
        return 5, "nenhum tests/test_*.py"
    with tempfile.TemporaryDirectory() as pasta:
        destino = Path(pasta)
        shutil.copy2(origem_modulo, destino / "descontos.py")
        shutil.copytree(DIR_TESTES, destino / "tests")
        ambiente = os.environ.copy()
        for chave in list(ambiente):
            if chave.startswith("PYTEST_"):
                ambiente.pop(chave, None)
        ambiente["PYTHONPATH"] = str(destino)
        ambiente["PYTHONIOENCODING"] = "utf-8"
        try:
            proc = subprocess.run(
                [
                    sys.executable,
                    "-m",
                    "pytest",
                    "-q",
                    "-p",
                    "no:cacheprovider",
                    "--rootdir",
                    str(destino),
                    "tests",
                ],
                cwd=destino,
                env=ambiente,
                capture_output=True,
                text=True,
                timeout=45,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            saida = (exc.stdout or "") + (exc.stderr or "")
            return 1, saida
        saida = (proc.stdout or "") + (proc.stderr or "")
        return proc.returncode, saida


def test_suite_passa_no_modulo_correto():
    codigo, saida = _executar(MODULO_CORRETO)
    assert codigo == 0, saida


@pytest.mark.parametrize("nome", MUTANTES)
def test_mutante_morto(nome):
    codigo, saida = _executar(DIR_MUTANTES / nome)
    assert codigo != 0, f"mutante {nome} sobreviveu\n{saida}"
