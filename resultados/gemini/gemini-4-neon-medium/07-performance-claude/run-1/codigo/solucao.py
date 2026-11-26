from itertools import accumulate, islice


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta subarrays contíguos não vazios de `nums` com soma `k` e
    comprimento em [comprimento_min, comprimento_max].
    """
    if comprimento_min < 1:
        raise ValueError("comprimento_min deve ser >= 1")
    if comprimento_max is not None and comprimento_max < 1:
        raise ValueError("comprimento_max deve ser >= 1")

    n = len(nums)
    if n == 0 or comprimento_min > n:
        return 0
    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0

    l_max = n if comprimento_max is None or comprimento_max > n else comprimento_max

    # Caso especial: sem restrições de comprimento (comprimento_min == 1 e sem limite efetivo)
    if comprimento_min == 1 and l_max == n:
        freq: dict[int, int] = {0: 1}
        freq_get = freq.get
        total = 0
        acc = 0
        for x in nums:
            acc += x
            total += freq_get(acc - k, 0)
            freq[acc] = freq_get(acc, 0) + 1
        return total

    prefix = list(accumulate(nums, initial=0))

    # Caso especial: comprimento fixo (janela de tamanho 1 sobre prefixos)
    if comprimento_min == l_max:
        total = 0
        for p_left, p_right in zip(prefix, islice(prefix, comprimento_min, None)):
            if p_right - p_left == k:
                total += 1
        return total

    # Caso sem remoção da janela (l_max == n)
    if l_max == n:
        freq = {}
        freq_get = freq.get
        total = 0
        for p_add, p_cur in zip(prefix, islice(prefix, comprimento_min, None)):
            freq[p_add] = freq_get(p_add, 0) + 1
            total += freq_get(p_cur - k, 0)
        return total

    # Caso geral: janela deslizante sobre prefixos com inserção e remoção
    freq = {}
    freq_get = freq.get
    total = 0

    # Fase 1: janela crescendo (r de comprimento_min até l_max)
    window_span = l_max - comprimento_min + 1
    for p_add, p_cur in zip(
        islice(prefix, 0, window_span),
        islice(prefix, comprimento_min, l_max + 1),
    ):
        freq[p_add] = freq_get(p_add, 0) + 1
        total += freq_get(p_cur - k, 0)

    # Fase 2: janela deslizando com tamanho fixo (r de l_max + 1 até n)
    for p_add, p_rem, p_cur in zip(
        islice(prefix, window_span, n - comprimento_min + 1),
        islice(prefix, 0, n - l_max),
        islice(prefix, l_max + 1, None),
    ):
        freq[p_add] = freq_get(p_add, 0) + 1
        rem_cnt = freq[p_rem]
        if rem_cnt == 1:
            del freq[p_rem]
        else:
            freq[p_rem] = rem_cnt - 1
        total += freq_get(p_cur - k, 0)

    return total
