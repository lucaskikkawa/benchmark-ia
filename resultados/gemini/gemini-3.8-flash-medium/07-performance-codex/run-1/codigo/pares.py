from collections import Counter


def contar_pares(valores, alvo: int) -> int:
    counts = Counter(valores)
    total = 0
    get = counts.get
    for x, c in counts.items():
        comp = alvo - x
        if x < comp:
            comp_count = get(comp, 0)
            if comp_count:
                total += c * comp_count
        elif x == comp:
            total += c * (c - 1) // 2
    return total
