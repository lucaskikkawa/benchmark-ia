def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta subarrays com soma ``k`` e comprimento dentro dos limites dados."""
    if comprimento_min < 1:
        raise ValueError("comprimento_min deve ser >= 1")
    if comprimento_max is not None and comprimento_max < 1:
        raise ValueError("comprimento_max deve ser >= 1")

    n = len(nums)
    if comprimento_min > n:
        return 0
    if comprimento_max is not None and comprimento_min > comprimento_max:
        return 0

    # prefixos[r] é a soma de nums[0:r]. Para cada fim r, os inícios
    # elegíveis são prefixos nos índices [r - comprimento_max, r - comprimento_min].
    prefixos = [0] * (n + 1)
    soma = 0
    for i, valor in enumerate(nums, 1):
        soma += valor
        prefixos[i] = soma

    frequencias: dict[int, int] = {}
    total = 0
    for fim in range(1, n + 1):
        entra = fim - comprimento_min
        if entra >= 0:
            valor = prefixos[entra]
            frequencias[valor] = frequencias.get(valor, 0) + 1

        if comprimento_max is not None:
            sai = fim - comprimento_max - 1
            if sai >= 0:
                valor = prefixos[sai]
                nova_freq = frequencias[valor] - 1
                if nova_freq:
                    frequencias[valor] = nova_freq
                else:
                    del frequencias[valor]

        total += frequencias.get(prefixos[fim] - k, 0)

    return total
