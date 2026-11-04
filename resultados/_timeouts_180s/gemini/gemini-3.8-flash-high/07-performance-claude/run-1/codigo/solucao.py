"""Solução para contagem de subarrays com soma exata e comprimento limitado."""

from collections import defaultdict
from itertools import accumulate


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta quantos subarrays contíguos não vazios de nums têm soma igual a k

    e comprimento no intervalo [comprimento_min, comprimento_max].

    Args:
        nums: Lista de inteiros.
        k: Soma alvo procurada.
        comprimento_min: Comprimento mínimo do subarray (padrão 1).
        comprimento_max: Comprimento máximo do subarray (None para ilimitado).

    Returns:
        Número de subarrays que satisfazem os critérios.

    Raises:
        ValueError: Se comprimento_min < 1 ou comprimento_max < 1 (se informado).
    """
    if comprimento_min < 1:
        raise ValueError("comprimento_min deve ser >= 1")
    if comprimento_max is not None and comprimento_max < 1:
        raise ValueError("comprimento_max deve ser >= 1")

    n = len(nums)
    if comprimento_min > n:
        return 0
    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0

    # Prefix sums: P[j] = sum(nums[:j])
    P = list(accumulate(nums, initial=0))
    freq: defaultdict[int, int] = defaultdict(int)
    ans = 0

    if comprimento_max is None or comprimento_max >= n:
        for j in range(comprimento_min, n + 1):
            freq[P[j - comprimento_min]] += 1
            ans += freq[P[j] - k]
    else:
        for j in range(comprimento_min, comprimento_max + 1):
            freq[P[j - comprimento_min]] += 1
            ans += freq[P[j] - k]
        for j in range(comprimento_max + 1, n + 1):
            freq[P[j - comprimento_min]] += 1
            freq[P[j - comprimento_max - 1]] -= 1
            ans += freq[P[j] - k]

    return ans
