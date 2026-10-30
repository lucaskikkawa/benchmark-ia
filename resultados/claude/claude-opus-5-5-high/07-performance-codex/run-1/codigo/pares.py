"""Contagem de pares (i < j) cuja soma é igual ao alvo, sem enumerá-los."""

from collections import Counter


def contar_pares(valores, alvo: int) -> int:
    """Conta pares de índices distintos i < j com valores[i] + valores[j] == alvo.

    Consome ``valores`` em uma única passagem (aceita geradores), sem modificá-lo
    e sem materializá-lo: guarda apenas a frequência de cada valor distinto.
    Tempo esperado O(n) e memória O(k), k = quantidade de valores distintos.
    """
    freq = Counter(valores)
    total = 0
    for v, c in freq.items():
        w = alvo - v
        if v < w:
            cw = freq.get(w)
            if cw:
                total += c * cw
        elif v == w:
            total += c * (c - 1) // 2
    return total
