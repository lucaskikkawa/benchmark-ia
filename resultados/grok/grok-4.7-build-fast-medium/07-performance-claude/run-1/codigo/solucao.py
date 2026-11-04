"""Conta subarrays contíguos com soma exata e comprimento limitado.

Para cada fim exclusivo r, os inícios válidos l formam a janela
[r - comprimento_max, r - comprimento_min]. Essa janela desliza um passo
por vez, então um mapa de frequências dos prefixos dentro dela responde
cada r em tempo amortizado O(1) (total O(n)), mesmo com negativos.
"""

from __future__ import annotations


def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    if comprimento_min < 1 or (comprimento_max is not None and comprimento_max < 1):
        raise ValueError("comprimento_min e comprimento_max devem ser >= 1")

    n = len(nums)
    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0
    if comprimento_min > n:
        return 0

    limite = n if comprimento_max is None or comprimento_max > n else comprimento_max
    minimo = comprimento_min

    prefixo = [0] * (n + 1)
    acumulado = 0
    for i, valor in enumerate(nums, 1):
        acumulado += valor
        prefixo[i] = acumulado

    frequencia: dict[int, int] = {}
    total = 0
    for fim in range(minimo, n + 1):
        inicio_entra = fim - minimo
        chave_entra = prefixo[inicio_entra]
        frequencia[chave_entra] = frequencia.get(chave_entra, 0) + 1

        inicio_sai = fim - limite - 1
        if inicio_sai >= 0:
            chave_sai = prefixo[inicio_sai]
            restante = frequencia[chave_sai] - 1
            if restante == 0:
                del frequencia[chave_sai]
            else:
                frequencia[chave_sai] = restante

        total += frequencia.get(prefixo[fim] - k, 0)

    return total
