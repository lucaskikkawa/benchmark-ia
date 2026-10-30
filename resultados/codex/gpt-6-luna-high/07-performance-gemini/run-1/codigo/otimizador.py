def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    """Retorna o maior comprimento de subarray contíguo com soma igual a alvo.

    Usa somas prefixadas e guarda a primeira posição de cada soma, permitindo
    encontrar o maior intervalo em uma única passagem pela lista.
    """
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")
    if type(alvo) is not int:
        raise TypeError("alvo deve ser um inteiro primitivo")
    for numero in numeros:
        if type(numero) is not int:
            raise TypeError("todos os elementos de numeros devem ser inteiros primitivos")

    primeira_posicao = {0: -1}
    soma_prefixada = 0
    maior_comprimento = 0

    for indice, numero in enumerate(numeros):
        soma_prefixada += numero
        posicao_inicial = primeira_posicao.get(soma_prefixada - alvo)
        if posicao_inicial is not None:
            comprimento = indice - posicao_inicial
            if comprimento > maior_comprimento:
                maior_comprimento = comprimento

        if soma_prefixada not in primeira_posicao:
            primeira_posicao[soma_prefixada] = indice

    return maior_comprimento
