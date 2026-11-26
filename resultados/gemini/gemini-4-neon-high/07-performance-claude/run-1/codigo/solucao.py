from itertools import accumulate, islice


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    if comprimento_min < 1:
        raise ValueError("comprimento_min deve ser >= 1")
    if comprimento_max is not None and comprimento_max < 1:
        raise ValueError("comprimento_max deve ser >= 1")

    n = len(nums)
    if n == 0 or comprimento_min > n:
        return 0
    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0

    if comprimento_max == comprimento_min:
        if comprimento_min == 1:
            return nums.count(k)
        prefix = list(accumulate(nums, initial=0))
        total = 0
        for p_l, p_r in zip(prefix, islice(prefix, comprimento_min, None)):
            if p_r - p_l == k:
                total += 1
        return total

    if comprimento_max is None or comprimento_max >= n:
        if comprimento_min == 1:
            counts: dict[int, int] = {0: 1}
            counts_get = counts.get
            soma = 0
            total = 0
            for x in nums:
                soma += x
                total += counts_get(soma - k, 0)
                counts[soma] = counts_get(soma, 0) + 1
            return total

        prefix = list(accumulate(nums, initial=0))
        counts = {}
        counts_get = counts.get
        total = 0
        for p_in, p_r in zip(prefix, islice(prefix, comprimento_min, None)):
            counts[p_in] = counts_get(p_in, 0) + 1
            total += counts_get(p_r - k, 0)
        return total

    prefix = list(accumulate(nums, initial=0))
    counts = {}
    counts_get = counts.get
    total = 0

    for p_in, p_r in zip(prefix, islice(prefix, comprimento_min, comprimento_max + 1)):
        counts[p_in] = counts_get(p_in, 0) + 1
        total += counts_get(p_r - k, 0)

    window_size = comprimento_max - comprimento_min + 1
    for p_in, p_out, p_r in zip(
        islice(prefix, window_size, None),
        prefix,
        islice(prefix, comprimento_max + 1, None),
    ):
        counts[p_in] = counts_get(p_in, 0) + 1
        rem = counts[p_out] - 1
        if rem:
            counts[p_out] = rem
        else:
            del counts[p_out]
        total += counts_get(p_r - k, 0)

    return total
