def contar_pares(valores, alvo: int) -> int:
    """Conta pares de índices (i, j) com i < j e valores[i] + valores[j] == alvo."""
    pares = 0
    vistos: dict[int, int] = {}
    for valor in valores:
        complemento = alvo - valor
        if complemento in vistos:
            pares += vistos[complemento]
        if valor in vistos:
            vistos[valor] += 1
        else:
            vistos[valor] = 1
    return pares
