"""Maior subarray contíguo com soma igual a um alvo, em O(N)."""


def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    if type(numeros) is not list:
        raise TypeError("numeros deve ser uma lista")
    if type(alvo) is not int:
        raise TypeError("alvo deve ser um inteiro")
    for x in numeros:
        if type(x) is not int:
            raise TypeError("todos os elementos de numeros devem ser inteiros")

    # Primeiro índice em que cada soma de prefixo aparece (prefixo vazio = -1).
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
