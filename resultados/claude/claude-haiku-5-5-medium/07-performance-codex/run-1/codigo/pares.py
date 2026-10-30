def contar_pares(valores, alvo: int) -> int:
    """Conta pares de índices distintos i < j com valores[i] + valores[j] == alvo.

    Passagem única sobre o iterável, sem materializá-lo. Tempo esperado O(n),
    memória O(k), k = quantidade de valores distintos.
    """
    contagem = {}
    pares = 0
    for valor in valores:
        # Consulta antes de inserir o valor atual: nenhum elemento forma par consigo mesmo.
        pares += contagem.get(alvo - valor, 0)
        contagem[valor] = contagem.get(valor, 0) + 1
    return pares
