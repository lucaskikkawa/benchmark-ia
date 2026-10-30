from collections import Counter
from typing import Iterable


def contar_pares(valores: Iterable[int], alvo: int) -> int:
    contagem = Counter(iter(valores))
    total = 0
    obter = contagem.get
    for valor, freq in contagem.items():
        complemento = alvo - valor
        if valor < complemento:
            freq_comp = obter(complemento)
            if freq_comp is not None:
                total += freq * freq_comp
        elif valor == complemento:
            total += freq * (freq - 1) // 2
    return total
