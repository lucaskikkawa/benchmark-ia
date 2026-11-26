from collections import Counter
from collections.abc import Iterable


def contar_pares(valores: Iterable[int], alvo: int) -> int:
    contagens = Counter(iter(valores))
    total = 0

    if alvo % 2 == 0:
        metade = alvo // 2
        qtd_metade = contagens.get(metade)
        if qtd_metade:
            total = qtd_metade * (qtd_metade - 1) // 2
        limite = metade
    else:
        limite = (alvo + 1) // 2

    contagens_get = contagens.get
    for valor, qtd in contagens.items():
        if valor < limite:
            qtd_comp = contagens_get(alvo - valor)
            if qtd_comp:
                total += qtd * qtd_comp

    return total
