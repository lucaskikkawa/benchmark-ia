from collections import Counter
from collections.abc import Iterable, Mapping


def contar_pares(valores: Iterable[int], alvo: int) -> int:
    """Conta pares de índices distintos (i, j) com i < j e valores[i] + valores[j] == alvo."""
    if isinstance(valores, Mapping):
        valores = iter(valores)

    contagem = Counter(valores)
    get = contagem.get
    total = 0

    for valor, qtd in contagem.items():
        complemento = alvo - valor
        if complemento > valor:
            qtd_comp = get(complemento)
            if qtd_comp is not None:
                total += qtd * qtd_comp
        elif complemento == valor:
            total += qtd * (qtd - 1) // 2

    return total
