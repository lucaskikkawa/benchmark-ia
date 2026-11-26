from collections.abc import Iterable


def contar_pares(valores: Iterable[int], alvo: int) -> int:
    """Conta pares de índices distintos (i, j) com i < j e valores[i] + valores[j] == alvo."""
    vistos: dict[int, int] = {}
    get = vistos.get
    total = 0
    for x in valores:
        complemento = alvo - x
        qtd = get(complemento)
        if qtd:
            total += qtd
        vistos[x] = get(x, 0) + 1
    return total
