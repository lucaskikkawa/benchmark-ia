from __future__ import annotations

import collections
import itertools


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta quantos subarrays contíguos não vazios de nums têm soma exatamente igual a k

    e comprimento entre comprimento_min e comprimento_max, inclusive.
    """
    if comprimento_min < 1:
        raise ValueError("comprimento_min deve ser >= 1")
    if comprimento_max is not None and comprimento_max < 1:
        raise ValueError("comprimento_max deve ser >= 1")
    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0

    n = len(nums)
    if comprimento_min > n:
        return 0

    # Prefix sums: P[0] = 0, P[i] = sum(nums[:i])
    p = list(itertools.accumulate(nums, initial=0))
    counts: dict[int, int] = collections.defaultdict(int)
    ans = 0

    if comprimento_max is None or comprimento_max >= n:
        for i in range(comprimento_min, n + 1):
            counts[p[i - comprimento_min]] += 1
            ans += counts.get(p[i] - k, 0)
    else:
        for i in range(comprimento_min, n + 1):
            counts[p[i - comprimento_min]] += 1
            if i > comprimento_max:
                val = p[i - comprimento_max - 1]
                c = counts[val] - 1
                if c == 0:
                    del counts[val]
                else:
                    counts[val] = c
            ans += counts.get(p[i] - k, 0)

    return ans
