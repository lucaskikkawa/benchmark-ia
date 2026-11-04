def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta subarrays cuja soma e comprimento estão dentro dos limites."""
    if comprimento_min < 1:
        raise ValueError("comprimento_min deve ser >= 1")
    if comprimento_max is not None and comprimento_max < 1:
        raise ValueError("comprimento_max deve ser >= 1")

    n = len(nums)
    if comprimento_min > n or (
        comprimento_max is not None and comprimento_min > comprimento_max
    ):
        return 0

    # prefixos[j] é a soma de nums[0:j]. Para um fim j, um subarray
    # elegível começa em i no intervalo [j - max, j - min].
    prefixos = [0] * (n + 1)
    for i, valor in enumerate(nums, 1):
        prefixos[i] = prefixos[i - 1] + valor

    frequencias: dict[int, int] = {}
    total = 0

    for fim in range(1, n + 1):
        entra = fim - comprimento_min
        if entra >= 0:
            soma = prefixos[entra]
            frequencias[soma] = frequencias.get(soma, 0) + 1

        if comprimento_max is not None:
            sai = fim - comprimento_max - 1
            if sai >= 0:
                soma = prefixos[sai]
                restante = frequencias[soma] - 1
                if restante:
                    frequencias[soma] = restante
                else:
                    del frequencias[soma]

        total += frequencias.get(prefixos[fim] - k, 0)

    return total
