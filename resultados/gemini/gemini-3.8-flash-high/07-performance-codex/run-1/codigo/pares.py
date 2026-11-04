from collections import Counter


def contar_pares(valores, alvo: int) -> int:
    """Conta pares de índices distintos (i, j) com i < j e valores[i] + valores[j] == alvo."""
    if hasattr(valores, "items"):
        valores = iter(valores)

    counts = Counter(valores)
    total = 0

    if alvo % 2 == 0:
        cnt = counts.get(alvo // 2, 0)
        total += cnt * (cnt - 1) // 2

    get_count = counts.get
    for x, count in counts.items():
        compl = alvo - x
        if x < compl:
            total += count * get_count(compl, 0)

    return total
