"""Contagem de subarrays contíguos com soma e comprimento limitados.

Prefixos + busca binária nos índices de cada soma: para o fim j, os inícios
válidos são os prefixos iguais a prefixo[j] - k cujo índice cai na janela
de comprimentos. O(n log n) e compatível com inteiros de magnitude arbitrária.
"""

from bisect import bisect_left, bisect_right


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    if comprimento_min < 1 or (comprimento_max is not None and comprimento_max < 1):
        raise ValueError("comprimento_min e comprimento_max devem ser >= 1")

    n = len(nums)
    if comprimento_min > n:
        return 0
    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0

    limite = n if comprimento_max is None or comprimento_max > n else comprimento_max
    minimo = comprimento_min

    # Índice i guarda a soma dos primeiros i elementos (i == 0 é o prefixo vazio).
    posicoes: dict[int, list[int]] = {0: [0]}
    prefixo = 0
    total = 0

    for j in range(1, n + 1):
        prefixo += nums[j - 1]
        hi = j - minimo
        if hi >= 0:
            lo = j - limite
            if lo < 0:
                lo = 0
            idxs = posicoes.get(prefixo - k)
            if idxs is not None:
                total += bisect_right(idxs, hi) - bisect_left(idxs, lo)
        bucket = posicoes.get(prefixo)
        if bucket is None:
            posicoes[prefixo] = [j]
        else:
            bucket.append(j)

    return total
