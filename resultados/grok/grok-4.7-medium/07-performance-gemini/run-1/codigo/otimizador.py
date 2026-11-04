def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    """Retorna o comprimento máximo de um subarray contíguo cuja soma é `alvo`.

    Tempo e espaço O(N) via somas prefixadas e o índice mais à esquerda de cada soma.
    """
    if type(numeros) is not list or type(alvo) is not int:
        raise TypeError

    # prefixo 0 ocorre imediatamente antes do início da lista
    primeiro_indice = {0: -1}
    prefixo = 0
    melhor = 0

    for i, valor in enumerate(numeros):
        if type(valor) is not int:
            raise TypeError
        prefixo += valor
        inicio = primeiro_indice.get(prefixo - alvo)
        if inicio is not None:
            tamanho = i - inicio
            if tamanho > melhor:
                melhor = tamanho
        # guarda só a primeira ocorrência para maximizar o comprimento
        if prefixo not in primeiro_indice:
            primeiro_indice[prefixo] = i

    return melhor
