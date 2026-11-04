def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    """Retorna o maior comprimento com soma alvo em tempo e espaço O(N)."""
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")
    if type(alvo) is not int:
        raise TypeError("alvo deve ser um inteiro primitivo")

    # Para cada soma prefixada, guardar a primeira posição maximiza a distância.
    primeiras_posicoes = {0: 0}
    soma = 0
    maior = 0

    for posicao, numero in enumerate(numeros, start=1):
        if type(numero) is not int:
            raise TypeError("cada elemento de numeros deve ser um inteiro primitivo")

        soma += numero
        inicio = primeiras_posicoes.get(soma - alvo)
        if inicio is not None:
            comprimento = posicao - inicio
            if comprimento > maior:
                maior = comprimento

        if soma not in primeiras_posicoes:
            primeiras_posicoes[soma] = posicao

    return maior
