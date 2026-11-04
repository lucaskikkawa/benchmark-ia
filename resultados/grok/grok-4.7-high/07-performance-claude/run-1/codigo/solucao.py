def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta subarrays contíguos com soma ``k`` e comprimento nos limites dados.

    Para cada fim ``j``, a soma ``prefixo[j] - prefixo[l] == k`` com
    ``j - comprimento_max <= l <= j - comprimento_min``. Os prefixos elegíveis
    entram e saem de uma janela deslizante de índices (cada índice uma vez).
    """
    if comprimento_min < 1 or (comprimento_max is not None and comprimento_max < 1):
        raise ValueError("comprimento_min e comprimento_max devem ser >= 1")

    n = len(nums)
    if comprimento_min > n or (
        comprimento_max is not None and comprimento_min > comprimento_max
    ):
        return 0

    if comprimento_max is None or comprimento_max > n:
        limite = n
    else:
        limite = comprimento_max

    prefixo = [0] * (n + 1)
    soma = 0
    for i in range(n):
        soma += nums[i]
        prefixo[i + 1] = soma

    freq: dict[int, int] = {}
    obter = freq.get
    total = 0

    if limite == n:
        for j in range(comprimento_min, n + 1):
            valor = prefixo[j - comprimento_min]
            freq[valor] = obter(valor, 0) + 1
            total += obter(prefixo[j] - k, 0)
        return total

    remover = 0
    for j in range(comprimento_min, n + 1):
        valor = prefixo[j - comprimento_min]
        freq[valor] = obter(valor, 0) + 1
        limite_esq = j - limite
        if remover < limite_esq:
            antigo = prefixo[remover]
            freq[antigo] -= 1
            remover += 1
        total += obter(prefixo[j] - k, 0)

    return total
