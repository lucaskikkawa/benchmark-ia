import json
import random
import subprocess
import sys
from pathlib import Path

import pytest

from solucao import contar_subarrays_soma

DIR_TRABALHO = Path(__file__).resolve().parent.parent
LIMITE_S = 2.0


def forca_bruta(nums, k):
    total = 0
    for i in range(len(nums)):
        soma = 0
        for j in range(i, len(nums)):
            soma += nums[j]
            total += soma == k
    return total


# Roda a chamada grande em subprocesso: uma solução O(n^2) é morta pelo timeout
# em vez de travar a suíte inteira. O tempo medido é só o da chamada.
SCRIPT_TEMPO = r"""
import json, random, sys, time
sys.path.insert(0, sys.argv[1])
from solucao import contar_subarrays_soma
caso = sys.argv[2]
n = 300_000
if caso == "zeros":
    nums, k = [0] * n, 0
elif caso == "uns":
    nums, k = [1] * n, 1000
else:
    rng = random.Random(12345)
    nums, k = [rng.randint(-10, 10) for _ in range(n)], 7
inicio = time.perf_counter()
resultado = contar_subarrays_soma(nums, k)
decorrido = time.perf_counter() - inicio
print(json.dumps({"resultado": resultado, "tempo": decorrido}))
"""


def oraculo_linear(nums, k):
    vistos = {0: 1}
    prefixo = total = 0
    for x in nums:
        prefixo += x
        total += vistos.get(prefixo - k, 0)
        vistos[prefixo] = vistos.get(prefixo, 0) + 1
    return total


def medir(caso):
    try:
        r = subprocess.run(
            [sys.executable, "-c", SCRIPT_TEMPO, str(DIR_TRABALHO), caso],
            capture_output=True, text=True, timeout=4 * LIMITE_S,
        )
    except subprocess.TimeoutExpired:
        pytest.fail(f"caso {caso!r} excedeu {4 * LIMITE_S:.0f}s (solução muito lenta)")
    assert r.returncode == 0, r.stderr
    return json.loads(r.stdout.strip().splitlines()[-1])


@pytest.mark.parametrize(
    "nums, k, esperado",
    [
        ([1, 1, 1], 2, 2),
        ([1, 2, 3], 3, 2),
        ([1, -1, 0], 0, 3),
        ([], 0, 0),
        ([], 5, 0),
        ([5], 5, 1),
        ([5], 4, 0),
        ([0, 0, 0], 0, 6),
        ([-1, -1, 1], -1, 3),
        ([3, 4, 7, 2, -3, 1, 4, 2], 7, 4),
    ],
)
def test_casos_pequenos(nums, k, esperado):
    assert contar_subarrays_soma(nums, k) == esperado


def test_aleatorio_contra_forca_bruta():
    rng = random.Random(2024)
    for _ in range(300):
        n = rng.randint(0, 40)
        nums = [rng.randint(-5, 5) for _ in range(n)]
        k = rng.randint(-8, 8)
        assert contar_subarrays_soma(nums, k) == forca_bruta(nums, k), (nums, k)


def test_nao_modifica_entrada():
    nums = [3, -1, 2, 0, 5]
    copia = list(nums)
    contar_subarrays_soma(nums, 2)
    assert nums == copia


def test_valores_grandes():
    nums = [10**12, -(10**12), 10**12]
    assert contar_subarrays_soma(nums, 10**12) == 3


def test_desempenho_zeros():
    medida = medir("zeros")
    n = 300_000
    assert medida["resultado"] == n * (n + 1) // 2
    assert medida["tempo"] < LIMITE_S, f"{medida['tempo']:.2f}s"


def test_desempenho_uns():
    medida = medir("uns")
    assert medida["resultado"] == 300_000 - 1000 + 1
    assert medida["tempo"] < LIMITE_S, f"{medida['tempo']:.2f}s"


def test_desempenho_aleatorio():
    rng = random.Random(12345)
    nums = [rng.randint(-10, 10) for _ in range(300_000)]
    medida = medir("aleatorio")
    assert medida["resultado"] == oraculo_linear(nums, 7)
    assert medida["tempo"] < LIMITE_S, f"{medida['tempo']:.2f}s"
