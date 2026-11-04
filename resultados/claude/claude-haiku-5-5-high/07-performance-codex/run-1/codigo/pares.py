def contar_pares(valores, alvo: int) -> int:
    """Conta pares de índices i < j com valores[i] + valores[j] == alvo.

    Percorre a entrada uma única vez, guardando quantas vezes cada valor já foi visto.
    Cada elemento só forma pares com os anteriores, então nenhum par é contado duas
    vezes e nenhum elemento é pareado consigo mesmo. Tempo esperado O(n), memória O(k).
    """
    vistos = {}
    pares = 0
    for x in valores:
        pares += vistos.get(alvo - x, 0)
        vistos[x] = vistos.get(x, 0) + 1
    return pares
