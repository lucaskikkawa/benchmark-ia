from collections import defaultdict
from itertools import accumulate


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    if comprimento_min < 1 or (comprimento_max is not None and comprimento_max < 1):
        raise ValueError("comprimento_min e comprimento_max devem ser >= 1")

    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0

    n = len(nums)
    if n == 0 or comprimento_min > n:
        return 0

    max_len = n if comprimento_max is None or comprimento_max > n else comprimento_max

    prefix = list(accumulate(nums, initial=0))
    freq: defaultdict[int, int] = defaultdict(int)
    get_freq = freq.get
    total = 0

    for r in range(comprimento_min, max_len + 1):
        freq[prefix[r - comprimento_min]] += 1
        c = get_freq(prefix[r] - k)
        if c:
            total += c

    step_out = max_len + 1
    for r in range(max_len + 1, n + 1):
        freq[prefix[r - comprimento_min]] += 1
        freq[prefix[r - step_out]] -= 1
        c = get_freq(prefix[r] - k)
        if c:
            total += c

    return total
