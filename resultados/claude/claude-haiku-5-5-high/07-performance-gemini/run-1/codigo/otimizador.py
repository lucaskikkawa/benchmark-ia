def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")
    if type(alvo) is not int:
        raise TypeError("alvo deve ser um inteiro primitivo")
    for x in numeros:
        if type(x) is not int:
            raise TypeError("todos os elementos de numeros devem ser inteiros primitivos")

    # Para cada soma de prefixo, guarda o menor índice em que ela aparece.
    # Um subarray numeros[k:j] soma alvo quando prefixo[j] - prefixo[k] == alvo,
    # e o menor k disponível produz o subarray mais longo que termina em j.
    primeira_ocorrencia = {0: 0}
    soma = 0
    maior = 0
    for j, x in enumerate(numeros, start=1):
        soma += x
        k = primeira_ocorrencia.get(soma - alvo)
        if k is not None and j - k > maior:
            maior = j - k
        primeira_ocorrencia.setdefault(soma, j)
    return maior
