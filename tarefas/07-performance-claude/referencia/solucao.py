"""Contagem de subarrays contíguos com soma exata e comprimento limitado, em O(n)."""

from collections import defaultdict


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta os subarrays contíguos de ``nums`` com soma ``k`` e comprimento em [min, max].

    Com somas de prefixo P (P[0] = 0), o trecho nums[i:j] tem soma P[j] - P[i] e
    comprimento j - i. Para cada fim j, os inícios válidos formam a janela
    i ∈ [j - max, j - min]; mantemos a contagem dos prefixos dessa janela,
    inserindo P[j - min] e removendo P[j - max - 1] a cada passo. Tempo O(n),
    memória O(n).

    Raises:
        ValueError: se ``comprimento_min < 1`` ou ``comprimento_max < 1``.
    """
    if comprimento_min < 1:
        raise ValueError(f"comprimento_min deve ser >= 1: {comprimento_min}")
    if comprimento_max is not None and comprimento_max < 1:
        raise ValueError(f"comprimento_max deve ser >= 1: {comprimento_max}")

    n = len(nums)
    maximo = n if comprimento_max is None else min(comprimento_max, n)
    if comprimento_min > maximo:
        return 0

    prefixos = [0] * (n + 1)
    for indice, valor in enumerate(nums):
        prefixos[indice + 1] = prefixos[indice] + valor

    na_janela: defaultdict[int, int] = defaultdict(int)
    total = 0
    for fim in range(comprimento_min, n + 1):
        na_janela[prefixos[fim - comprimento_min]] += 1
        saindo = fim - maximo - 1
        if saindo >= 0:
            na_janela[prefixos[saindo]] -= 1
        total += na_janela[prefixos[fim] - k]
    return total
