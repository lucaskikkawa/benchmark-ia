def contar_pares(valores, alvo: int) -> int:
    """Conta pares i < j com valores[i] + valores[j] == alvo.

    Uma passagem: cada valor novo forma par com as ocorrências já vistas
    do complemento. Tempo esperado O(n), memória O(k).
    """
    freq = {}
    total = 0
    for v in valores:
        total += freq.get(alvo - v, 0)
        freq[v] = freq.get(v, 0) + 1
    return total
