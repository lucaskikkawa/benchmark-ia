def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    """Retorna o comprimento máximo de um subarray contíguo cuja soma é `alvo`.

    Complexidade O(N) em tempo e espaço via somas de prefixo. A primeira
    ocorrência de cada prefixo é guardada para maximizar o intervalo.
    """
    if type(numeros) is not list:
        raise TypeError("numeros deve ser uma list")
    if type(alvo) is not int:
        raise TypeError("alvo deve ser um int primitivo")

    # prefixo 0 ocorre antes do início, para cobrir subarrays que começam em 0
    primeira_ocorrencia = {0: -1}
    soma = 0
    melhor = 0

    for i, valor in enumerate(numeros):
        if type(valor) is not int:
            raise TypeError("cada elemento de numeros deve ser um int primitivo")
        soma += valor
        inicio = primeira_ocorrencia.get(soma - alvo)
        if inicio is not None:
            tamanho = i - inicio
            if tamanho > melhor:
                melhor = tamanho
        if soma not in primeira_ocorrencia:
            primeira_ocorrencia[soma] = i

    return melhor
