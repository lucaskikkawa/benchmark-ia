def contar_pares(valores, alvo: int) -> int:
    """Conta pares (i, j), i < j, com valores[i] + valores[j] == alvo.

    Uma passagem, tempo esperado O(n), memória O(k) para k valores distintos.
    """
    freq = {}
    total = 0
    obter = freq.get
    for valor in valores:
        total += obter(alvo - valor, 0)
        freq[valor] = obter(valor, 0) + 1
    return total
