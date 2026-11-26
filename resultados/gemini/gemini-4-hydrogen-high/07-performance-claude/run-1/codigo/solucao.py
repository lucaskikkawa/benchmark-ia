from collections import defaultdict
from itertools import accumulate, islice


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta subarrays contíguos não vazios com soma == k e comprimento no intervalo dado."""
    if comprimento_min < 1:
        raise ValueError("comprimento_min deve ser >= 1")
    if comprimento_max is not None and comprimento_max < 1:
        raise ValueError("comprimento_max deve ser >= 1")

    n = len(nums)
    if comprimento_min > n:
        return 0
    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0

    l_max = n if comprimento_max is None or comprimento_max > n else comprimento_max

    if comprimento_min == l_max:
        if comprimento_min == 1:
            return nums.count(k)
        window_sum = sum(islice(nums, comprimento_min))
        total = 1 if window_sum == k else 0
        for add_val, rem_val in zip(islice(nums, comprimento_min, None), nums):
            window_sum += add_val - rem_val
            if window_sum == k:
                total += 1
        return total

    if comprimento_min == 1 and l_max == n:
        counts: defaultdict[int, int] = defaultdict(int)
        counts[0] = 1
        counts_get = counts.get
        prefix = 0
        total = 0
        for x in nums:
            prefix += x
            total += counts_get(prefix - k, 0)
            counts[prefix] += 1
        return total

    prefixes = list(accumulate(nums, initial=0))
    counts = defaultdict(int)
    counts_get = counts.get
    total = 0

    if l_max == n:
        for p_r, p_add in zip(islice(prefixes, comprimento_min, None), prefixes):
            counts[p_add] += 1
            total += counts_get(p_r - k, 0)
        return total

    for p_r, p_add in zip(islice(prefixes, comprimento_min, l_max + 1), prefixes):
        counts[p_add] += 1
        total += counts_get(p_r - k, 0)

    for p_r, p_add, p_rem in zip(
        islice(prefixes, l_max + 1, None),
        islice(prefixes, l_max + 1 - comprimento_min, None),
        prefixes,
    ):
        counts[p_add] += 1
        rem_count = counts[p_rem]
        if rem_count == 1:
            del counts[p_rem]
        else:
            counts[p_rem] = rem_count - 1
        total += counts_get(p_r - k, 0)

    return total
