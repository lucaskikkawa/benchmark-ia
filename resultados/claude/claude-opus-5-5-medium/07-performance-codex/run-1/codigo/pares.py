"""Contagem de pares (i < j) com soma igual a um alvo, em uma única passagem."""


def contar_pares(valores, alvo: int) -> int:
    """Conta pares de índices i < j com valores[i] + valores[j] == alvo.

    Tempo esperado O(n) e memória O(k), k = quantidade de valores distintos.
    Aceita qualquer iterável finito, inclusive geradores de uma passagem.
    """
    vistos = {}
    get = vistos.get
    total = 0
    for x in valores:
        total += get(alvo - x, 0)
        vistos[x] = get(x, 0) + 1
    return total
