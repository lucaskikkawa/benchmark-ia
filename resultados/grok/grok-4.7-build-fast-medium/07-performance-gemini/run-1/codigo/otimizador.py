def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    """Retorna o comprimento do maior subarray contíguo cuja soma é `alvo`.

    Tempo e espaço O(N) via soma de prefixos e a primeira posição de cada soma.
    """
    if type(numeros) is not list or type(alvo) is not int:
        raise TypeError

    # prefixo 0 ocorre antes do início (índice -1).
    primeira = {0: -1}
    prefixo = 0
    melhor = 0

    for i, valor in enumerate(numeros):
        if type(valor) is not int:
            raise TypeError
        prefixo += valor
        inicio = primeira.get(prefixo - alvo)
        if inicio is not None:
            tamanho = i - inicio
            if tamanho > melhor:
                melhor = tamanho
        # Mantém a ocorrência mais antiga para maximizar o comprimento.
        if prefixo not in primeira:
            primeira[prefixo] = i

    return melhor
