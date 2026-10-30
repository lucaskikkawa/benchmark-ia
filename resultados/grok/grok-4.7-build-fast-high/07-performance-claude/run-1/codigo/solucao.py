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
    if comprimento_max is None or comprimento_max > n:
        comprimento_max = n

    prefixos = [0] * (n + 1)
    soma = 0
    for i, valor in enumerate(nums):
        soma += valor
        prefixos[i + 1] = soma

    freq: dict[int, int] = {}
    resposta = 0
    esquerda = 0
    obter = freq.get

    for direita in range(comprimento_min, n + 1):
        indice = direita - comprimento_min
        valor_prefixo = prefixos[indice]
        freq[valor_prefixo] = obter(valor_prefixo, 0) + 1

        limite = direita - comprimento_max
        while esquerda < limite:
            antigo = prefixos[esquerda]
            contagem = freq[antigo] - 1
            if contagem == 0:
                del freq[antigo]
            else:
                freq[antigo] = contagem
            esquerda += 1

        resposta += obter(prefixos[direita] - k, 0)

    return resposta
