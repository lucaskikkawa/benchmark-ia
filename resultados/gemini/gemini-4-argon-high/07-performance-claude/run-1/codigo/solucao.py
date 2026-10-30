from collections import defaultdict
from itertools import accumulate


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta subarrays contíguos não vazios de `nums` com soma `k` e comprimento no intervalo dado."""
    if comprimento_min < 1:
        raise ValueError("comprimento_min deve ser >= 1")
    if comprimento_max is not None and comprimento_max < 1:
        raise ValueError("comprimento_max deve ser >= 1")

    n = len(nums)
    if n == 0 or comprimento_min > n:
        return 0
    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0

    if comprimento_max is None or comprimento_max >= n:
        if comprimento_min == 1:
            freq: defaultdict[int, int] = defaultdict(int)
            freq[0] = 1
            get = freq.get
            total = 0
            for s in accumulate(nums):
                total += get(s - k, 0)
                freq[s] += 1
            return total

        prefix = list(accumulate(nums, initial=0))
        freq = defaultdict(int)
        get = freq.get
        total = 0
        for p_add, p_r in zip(prefix, prefix[comprimento_min:]):
            freq[p_add] += 1
            total += get(p_r - k, 0)
        return total

    if comprimento_min == comprimento_max:
        if comprimento_min == 1:
            return nums.count(k)
        prefix = list(accumulate(nums, initial=0))
        return sum(
            1 for p_l, p_r in zip(prefix, prefix[comprimento_min:]) if p_r - p_l == k
        )

    prefix = list(accumulate(nums, initial=0))
    freq = defaultdict(int)
    get = freq.get
    total = 0
    janela = comprimento_max - comprimento_min + 1

    for p_add, p_r in zip(
        prefix[:janela], prefix[comprimento_min : comprimento_max + 1]
    ):
        freq[p_add] += 1
        total += get(p_r - k, 0)

    for p_rem, p_add, p_r in zip(
        prefix,
        prefix[janela:],
        prefix[comprimento_max + 1 :],
    ):
        freq[p_rem] -= 1
        freq[p_add] += 1
        total += get(p_r - k, 0)

    return total
