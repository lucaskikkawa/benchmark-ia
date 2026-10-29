"""Contagem de subarrays contíguos com soma exata em O(n)."""

from collections import defaultdict


def contar_subarrays_soma(nums: list[int], k: int) -> int:
    """Conta os subarrays contíguos não vazios de ``nums`` cuja soma é ``k``.

    Usa somas de prefixo: o trecho (i, j] soma ``k`` quando
    ``prefixo[j] - prefixo[i] == k``. Guardando quantas vezes cada prefixo
    já apareceu, cada posição é resolvida em O(1). Tempo O(n), memória O(n).
    """
    ocorrencias_prefixo: defaultdict[int, int] = defaultdict(int)
    ocorrencias_prefixo[0] = 1  # prefixo vazio
    prefixo = 0
    total = 0
    for valor in nums:
        prefixo += valor
        total += ocorrencias_prefixo[prefixo - k]
        ocorrencias_prefixo[prefixo] += 1
    return total
