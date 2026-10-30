def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    """Retorna o maior comprimento com soma alvo em tempo e espaço O(N)."""
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")
    if type(alvo) is not int:
        raise TypeError("alvo deve ser um inteiro primitivo")

    # Preservar a primeira posição de cada soma maximiza o comprimento.
    primeiras_posicoes = {0: -1}
    soma = 0
    maior = 0

    for indice, numero in enumerate(numeros):
        if type(numero) is not int:
            raise TypeError("cada elemento de numeros deve ser um inteiro primitivo")

        soma += numero
        inicio = primeiras_posicoes.get(soma - alvo)
        if inicio is not None:
            comprimento = indice - inicio
            if comprimento > maior:
                maior = comprimento
        primeiras_posicoes.setdefault(soma, indice)

    return maior
