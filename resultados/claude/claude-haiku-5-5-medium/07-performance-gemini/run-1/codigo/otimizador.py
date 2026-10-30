def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    """Retorna o comprimento do maior subarray contíguo cuja soma é exatamente `alvo`.

    Usa somas de prefixo: o subarray numeros[i:j] soma `alvo` se, e somente se,
    prefixo[j] - prefixo[i] == alvo. Guardando apenas a primeira ocorrência de
    cada valor de prefixo, obtém-se o maior j - i para cada j. Complexidade O(N).
    """
    if type(numeros) is not list:
        raise TypeError("numeros deve ser uma lista")
    if type(alvo) is not int:
        raise TypeError("alvo deve ser um int primitivo")

    primeira_ocorrencia = {0: -1}
    prefixo = 0
    maior = 0

    for j, x in enumerate(numeros):
        if type(x) is not int:
            raise TypeError("todos os elementos de numeros devem ser int primitivos")
        prefixo += x
        i = primeira_ocorrencia.get(prefixo - alvo)
        if i is not None and j - i > maior:
            maior = j - i
        if prefixo not in primeira_ocorrencia:
            primeira_ocorrencia[prefixo] = j

    return maior
