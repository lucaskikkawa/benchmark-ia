"""Módulo com a função contar_subarrays_soma."""

from __future__ import annotations


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta quantos subarrays contíguos não vazios de nums têm soma igual a k

    e comprimento entre comprimento_min e comprimento_max (inclusive).
    """
    if isinstance(comprimento_min, bool) or not isinstance(comprimento_min, (int, float)) or comprimento_min < 1:
        raise ValueError("comprimento_min deve ser >= 1")
    if isinstance(comprimento_min, float):
        if not comprimento_min.is_integer():
            raise ValueError("comprimento_min deve ser um inteiro")
        comprimento_min = int(comprimento_min)

    if comprimento_max is not None:
        if isinstance(comprimento_max, bool) or not isinstance(comprimento_max, (int, float)) or comprimento_max < 1:
            raise ValueError("comprimento_max deve ser >= 1")
        if comprimento_max == float("inf"):
            comprimento_max = None
        elif isinstance(comprimento_max, float):
            if not comprimento_max.is_integer():
                raise ValueError("comprimento_max deve ser um inteiro")
            comprimento_max = int(comprimento_max)

    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0

    n = len(nums)
    if comprimento_min > n:
        return 0

    # Prefix sums: P[x] = sum(nums[0:x]), P[0] = 0
    # A subarray nums[i:j] (comprimento j - i) tem soma P[j] - P[i] == k <=> P[i] == P[j] - k.
    P = [0] * (n + 1)
    s = 0
    for i, x in enumerate(nums):
        s += x
        P[i + 1] = s

    freq: dict[int, int] = {}
    ans = 0

    if comprimento_max is None:
        for j in range(comprimento_min, n + 1):
            add_val = P[j - comprimento_min]
            freq[add_val] = freq.get(add_val, 0) + 1
            ans += freq.get(P[j] - k, 0)
    else:
        split_point = min(n, comprimento_max)
        for j in range(comprimento_min, split_point + 1):
            add_val = P[j - comprimento_min]
            freq[add_val] = freq.get(add_val, 0) + 1
            ans += freq.get(P[j] - k, 0)

        for j in range(split_point + 1, n + 1):
            add_val = P[j - comprimento_min]
            freq[add_val] = freq.get(add_val, 0) + 1
            rem_val = P[j - comprimento_max - 1]
            c = freq[rem_val]
            if c == 1:
                del freq[rem_val]
            else:
                freq[rem_val] = c - 1
            ans += freq.get(P[j] - k, 0)

    return ans
