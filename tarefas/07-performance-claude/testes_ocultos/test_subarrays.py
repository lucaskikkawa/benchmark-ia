import json
import random
import subprocess
import sys
from pathlib import Path

import pytest

from solucao import contar_subarrays_soma

DIR_TRABALHO = Path(__file__).resolve().parent.parent
LIMITE_S = 2.0


def forca_bruta(nums, k, cmin=1, cmax=None):
    total = 0
    for i in range(len(nums)):
        soma = 0
        for j in range(i, len(nums)):
            soma += nums[j]
            comprimento = j - i + 1
            if comprimento >= cmin and (cmax is None or comprimento <= cmax):
                total += soma == k
    return total


def pares_de_zeros(n, cmin, cmax):
    """Quantidade de subarrays de [0]*n com comprimento em [cmin, cmax]."""
    return sum(n - c + 1 for c in range(cmin, min(cmax, n) + 1))


# Roda a chamada grande em subprocesso: uma solução O(n^2) é morta pelo timeout
# em vez de travar a suíte inteira. O tempo medido é só o da chamada.
SCRIPT_TEMPO = r"""
import json, random, sys, time
sys.path.insert(0, sys.argv[1])
from solucao import contar_subarrays_soma
caso = sys.argv[2]
n = 300_000
kwargs = {}
if caso == "zeros":
    nums, k = [0] * n, 0
elif caso == "uns":
    nums, k = [1] * n, 1000
elif caso == "zeros_janela":
    nums, k, kwargs = [0] * n, 0, {"comprimento_min": 2_000, "comprimento_max": 7_000}
elif caso == "aleatorio_max":
    rng = random.Random(777)
    nums, k, kwargs = [rng.randint(-3, 3) for _ in range(n)], 0, {"comprimento_max": 5_000}
elif caso == "aleatorio_min":
    rng = random.Random(888)
    nums, k, kwargs = [rng.randint(-3, 3) for _ in range(n)], 0, {"comprimento_min": 3_000}
elif caso == "gigantes":
    rng = random.Random(999)
    nums, k, kwargs = [rng.choice((-1, 1)) * 2**70 for _ in range(n)], 0, {"comprimento_min": 2, "comprimento_max": 4_000}
else:
    rng = random.Random(12345)
    nums, k = [rng.randint(-10, 10) for _ in range(n)], 7
inicio = time.perf_counter()
resultado = contar_subarrays_soma(nums, k, **kwargs)
decorrido = time.perf_counter() - inicio
print(json.dumps({"resultado": resultado, "tempo": decorrido}))
"""


def oraculo_linear(nums, k, cmin=1, cmax=None):
    """Oráculo independente: prefixos agrupados por valor + busca binária nos índices."""
    import bisect

    n = len(nums)
    cmax = n if cmax is None else cmax
    posicoes = {}
    prefixo = 0
    prefixos = [0]
    for x in nums:
        prefixo += x
        prefixos.append(prefixo)
    for i, p in enumerate(prefixos):
        posicoes.setdefault(p, []).append(i)
    total = 0
    for j in range(1, n + 1):
        lista = posicoes.get(prefixos[j] - k)
        if lista:
            # inícios i com j - cmax <= i <= j - cmin
            total += max(0, bisect.bisect_right(lista, j - cmin) - bisect.bisect_left(lista, j - cmax))
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


@pytest.mark.parametrize(
    "nums, k, cmin, cmax, esperado",
    [
        ([1, -1, 0], 0, 2, None, 2),
        ([1, -1, 0], 0, 1, 2, 2),
        ([0, 0, 0], 0, 2, 2, 2),
        ([0, 0, 0], 0, 3, 3, 1),
        ([0, 0, 0], 0, 4, None, 0),
        ([0, 0, 0], 0, 3, 2, 0),
        ([5], 5, 1, 1, 1),
        ([], 0, 1, 1, 0),
        ([2, 2, 2, 2], 4, 1, 8, 3),
    ],
)
def test_limites_de_comprimento_pequenos(nums, k, cmin, cmax, esperado):
    assert contar_subarrays_soma(nums, k, cmin, cmax) == esperado
    assert contar_subarrays_soma(nums, k, comprimento_min=cmin, comprimento_max=cmax) == esperado


def test_limites_de_comprimento_contra_forca_bruta():
    rng = random.Random(4242)
    for _ in range(400):
        n = rng.randint(0, 30)
        nums = [rng.randint(-4, 4) for _ in range(n)]
        k = rng.randint(-6, 6)
        cmin = rng.randint(1, 8)
        cmax = rng.choice([None, rng.randint(1, 12)])
        assert contar_subarrays_soma(nums, k, cmin, cmax) == forca_bruta(nums, k, cmin, cmax), (nums, k, cmin, cmax)


@pytest.mark.parametrize("kwargs", [{"comprimento_min": 0}, {"comprimento_min": -2}, {"comprimento_max": 0}, {"comprimento_max": -5}])
def test_limites_invalidos(kwargs):
    with pytest.raises(ValueError):
        contar_subarrays_soma([1, 2, 3], 3, **kwargs)


def test_limites_invalidos_mesmo_com_lista_vazia():
    with pytest.raises(ValueError):
        contar_subarrays_soma([], 0, comprimento_max=0)
    with pytest.raises(ValueError):
        contar_subarrays_soma([], 0, comprimento_min=0)


def test_inteiros_maiores_que_64_bits():
    g = 2**64
    nums = [g, -g, g, g + 1, -1]
    for cmin, cmax in [(1, None), (2, 3), (1, 1), (3, 5)]:
        for k in (0, g, 2 * g, g + 1):
            assert contar_subarrays_soma(nums, k, cmin, cmax) == forca_bruta(nums, k, cmin, cmax)


def test_nao_modifica_entrada():
    nums = [3, -1, 2, 0, 5]
    copia = list(nums)
    contar_subarrays_soma(nums, 2)
    contar_subarrays_soma(nums, 2, 2, 3)
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


def test_desempenho_zeros_com_janela():
    medida = medir("zeros_janela")
    assert medida["resultado"] == pares_de_zeros(300_000, 2_000, 7_000)
    assert medida["tempo"] < LIMITE_S, f"{medida['tempo']:.2f}s"


def test_desempenho_aleatorio_com_max():
    rng = random.Random(777)
    nums = [rng.randint(-3, 3) for _ in range(300_000)]
    medida = medir("aleatorio_max")
    assert medida["resultado"] == oraculo_linear(nums, 0, 1, 5_000)
    assert medida["tempo"] < LIMITE_S, f"{medida['tempo']:.2f}s"


def test_desempenho_aleatorio_com_min():
    rng = random.Random(888)
    nums = [rng.randint(-3, 3) for _ in range(300_000)]
    medida = medir("aleatorio_min")
    assert medida["resultado"] == oraculo_linear(nums, 0, 3_000)
    assert medida["tempo"] < LIMITE_S, f"{medida['tempo']:.2f}s"


def test_desempenho_inteiros_gigantes_com_janela():
    rng = random.Random(999)
    nums = [rng.choice((-1, 1)) * 2**70 for _ in range(300_000)]
    medida = medir("gigantes")
    assert medida["resultado"] == oraculo_linear(nums, 0, 2, 4_000)
    assert medida["tempo"] < LIMITE_S, f"{medida['tempo']:.2f}s"
