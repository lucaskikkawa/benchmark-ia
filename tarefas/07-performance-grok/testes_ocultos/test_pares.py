import json
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from solucao import pares_com_soma


def test_vazio_e_um_elemento():
    assert pares_com_soma([], 0) == 0
    assert pares_com_soma([5], 10) == 0
    assert pares_com_soma([0], 0) == 0


def test_um_par_simples():
    assert pares_com_soma([1, 2, 3], 4) == 1
    assert pares_com_soma([1, 3], 4) == 1
    assert pares_com_soma([3, 1], 4) == 1


def test_duplicatas_cruzadas():
    assert pares_com_soma([1, 3, 1, 3], 4) == 4
    assert pares_com_soma([5, 5, 5], 10) == 3
    assert pares_com_soma([2, 2, 2], 4) == 3


def test_zeros():
    assert pares_com_soma([0, 0, 0, 0], 0) == 6
    assert pares_com_soma([0, 0], 0) == 1
    assert pares_com_soma([0, 1, 0], 0) == 1


def test_negativos():
    assert pares_com_soma([-2, 0, 2, -2], 0) == 2
    assert pares_com_soma([-5, -1, 3, 4], -2) == 1
    assert pares_com_soma([-3, -3, -3], -6) == 3


def test_sem_pares_e_alvo_zero_sem_simetria():
    assert pares_com_soma([1, 2, 3], 100) == 0
    assert pares_com_soma([1, 2, 3], 0) == 0


def test_nao_altera_a_lista():
    nums = [3, 1, 2, 3]
    copia = list(nums)
    assert pares_com_soma(nums, 4) == 2
    assert nums == copia


def test_confere_com_forca_bruta_em_amostra():
    nums = [(-1) ** i * (i % 17) for i in range(80)]
    for alvo in (-10, 0, 4, 15):
        assert pares_com_soma(nums, alvo) == _bruto(nums, alvo)


def test_tipos_invalidos():
    with pytest.raises(TypeError):
        pares_com_soma((1, 2), 3)
    with pytest.raises(TypeError):
        pares_com_soma(None, 0)
    with pytest.raises(TypeError):
        pares_com_soma([1, True], 2)
    with pytest.raises(TypeError):
        pares_com_soma([1, 2.0], 3)
    with pytest.raises(TypeError):
        pares_com_soma([1, 2], True)
    with pytest.raises(TypeError):
        pares_com_soma([1], "2")


def test_produto_de_grupos_grandes_sem_materializar():
    n = 20_000
    nums = [1] * n + [2] * n
    assert pares_com_soma(nums, 3) == n * n


SCRIPT_PERF = """
import json, sys, time
sys.path.insert(0, sys.argv[1])
from solucao import pares_com_soma

caso = sys.argv[2]
n = 100_000
if caso == "zeros":
    nums = [0] * n
    alvo = 0
    esperado = n * (n - 1) // 2
else:
    nums = list(range(n))
    alvo = n - 1
    esperado = n // 2

inicio = time.perf_counter()
resultado = pares_com_soma(nums, alvo)
duracao = time.perf_counter() - inicio
preservou = (nums == ([0] * n if caso == "zeros" else list(range(n))))
print(json.dumps([resultado, duracao, esperado, preservou]))
"""


def _medir(caso):
    dir_trabalho = Path(__file__).resolve().parents[1]
    env = {**os.environ, "PYTHONIOENCODING": "utf-8"}
    try:
        proc = subprocess.run(
            [sys.executable, "-c", SCRIPT_PERF, str(dir_trabalho), caso],
            cwd=dir_trabalho,
            env=env,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(f"caso {caso!r} excedeu o limite de 5s (solução muito lenta)")
    assert proc.returncode == 0, proc.stderr
    return json.loads(proc.stdout.strip().splitlines()[-1])


def test_performance_cem_mil():
    for caso in ("zeros", "sequencia"):
        resultado, duracao, esperado, preservou = _medir(caso)
        assert resultado == esperado
        assert duracao < 2.0, f"caso {caso} levou {duracao:.3f}s (limite 2.0s)"
        assert preservou is True


def _bruto(nums, alvo):
    total = 0
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == alvo:
                total += 1
    return total
