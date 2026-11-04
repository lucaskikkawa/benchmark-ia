def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    """Retorna o maior comprimento de subarray cuja soma é ``alvo``.

    Usa somas de prefixo e registra a primeira posição de cada soma. Assim,
    cada elemento é processado uma única vez, inclusive quando há negativos.
    """
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")
    if type(alvo) is not int:
        raise TypeError("alvo deve ser um inteiro")

    primeira_posicao = {0: -1}
    soma_prefixo = 0
    maior = 0

    for indice, numero in enumerate(numeros):
        if type(numero) is not int:
            raise TypeError("todos os elementos de numeros devem ser inteiros")

        soma_prefixo += numero
        inicio_prefixo = primeira_posicao.get(soma_prefixo - alvo)
        if inicio_prefixo is not None:
            comprimento = indice - inicio_prefixo
            if comprimento > maior:
                maior = comprimento

        # Manter apenas a ocorrência mais antiga maximiza o subarray futuro.
        if soma_prefixo not in primeira_posicao:
            primeira_posicao[soma_prefixo] = indice

    return maior
