"""Contagem de subarrays por soma e intervalo de comprimentos."""

from itertools import accumulate


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta trechos não vazios em tempo esperado O(n) e espaço O(n).

    Para cada fim exclusivo, o mapa contém as somas prefixadas dos
    inícios que satisfazem os limites de comprimento. Um trecho tem soma
    k quando a soma prefixada de seu início é a do fim menos k.
    Os cálculos usam inteiros Python, sem truncamento ou conversão.
    """
    if comprimento_min < 1:
        raise ValueError("comprimento_min deve ser >= 1")
    if comprimento_max is not None and comprimento_max < 1:
        raise ValueError("comprimento_max deve ser >= 1")

    n = len(nums)
    if comprimento_min > n:
        return 0
    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0

    prefixos = list(accumulate(nums, initial=0))
    frequencias: dict[int, int] = {}
    obter = frequencias.get
    total = 0

    if comprimento_max is None or comprimento_max >= n:
        for fim in range(comprimento_min, n + 1):
            entrada = prefixos[fim - comprimento_min]
            frequencias[entrada] = obter(entrada, 0) + 1
            total += obter(prefixos[fim] - k, 0)
    else:
        for fim in range(comprimento_min, n + 1):
            entrada = prefixos[fim - comprimento_min]
            frequencias[entrada] = obter(entrada, 0) + 1

            if fim > comprimento_max:
                saida = prefixos[fim - comprimento_max - 1]
                restante = frequencias[saida] - 1
                if restante:
                    frequencias[saida] = restante
                else:
                    del frequencias[saida]

            total += obter(prefixos[fim] - k, 0)

    return total
