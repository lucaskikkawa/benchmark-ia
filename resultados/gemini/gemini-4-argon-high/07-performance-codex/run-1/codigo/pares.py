from collections import Counter
from collections.abc import Iterable


def contar_pares(valores: Iterable[int], alvo: int) -> int:
    contagem = Counter(iter(valores))
    obter = contagem.get
    total_duplo = 0
    for valor, qtd in contagem.items():
        complemento = alvo - valor
        if complemento == valor:
            total_duplo += qtd * (qtd - 1)
        else:
            qtd_comp = obter(complemento)
            if qtd_comp is not None:
                total_duplo += qtd * qtd_comp
    return total_duplo // 2
