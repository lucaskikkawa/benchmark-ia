def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    """Retorna o comprimento do maior subarray contíguo cuja soma é `alvo`.

    Usa somas de prefixo com um dicionário que guarda o primeiro índice em
    que cada soma de prefixo aparece: O(N) de tempo e espaço.
    """
    if type(numeros) is not list:
        raise TypeError("numeros deve ser uma lista")
    for x in numeros:
        if type(x) is not int:
            raise TypeError("todos os elementos de numeros devem ser int")
    if type(alvo) is not int:
        raise TypeError("alvo deve ser int")

    primeiro = {0: -1}
    soma = 0
    melhor = 0
    for i, x in enumerate(numeros):
        soma += x
        j = primeiro.get(soma - alvo)
        if j is not None and i - j > melhor:
            melhor = i - j
        if soma not in primeiro:
            primeiro[soma] = i
    return melhor
