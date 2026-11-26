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
    if comprimento_min > n or (comprimento_max is not None and comprimento_min > comprimento_max):
        return 0

    prefix = list(accumulate(nums, initial=0))
    freq: dict[int, int] = {}
    freq_get = freq.get
    total = 0

    if comprimento_max is None or comprimento_max >= n:
        for p_in, p_cur in zip(prefix, prefix[comprimento_min:]):
            freq[p_in] = freq_get(p_in, 0) + 1
            total += freq_get(p_cur - k, 0)
        return total

    for p_in, p_cur in zip(prefix, prefix[comprimento_min : comprimento_max + 1]):
        freq[p_in] = freq_get(p_in, 0) + 1
        total += freq_get(p_cur - k, 0)

    offset_in = comprimento_max + 1 - comprimento_min
    for p_in, p_out, p_cur in zip(
        prefix[offset_in:],
        prefix,
        prefix[comprimento_max + 1 :],
    ):
        freq[p_in] = freq_get(p_in, 0) + 1
        cnt = freq[p_out] - 1
        if cnt == 0:
            del freq[p_out]
        else:
            freq[p_out] = cnt
        total += freq_get(p_cur - k, 0)

    return total
