def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    """Retorna o comprimento do maior subarray contíguo cuja soma seja igual a alvo.

    Complexidade de tempo: O(N) usando mapa de somas acumuladas.
    Complexidade de espaço: O(N).
    """
    soma_acumulada = 0
    maior_comprimento = 0
    primeira_ocorrencia = {0: -1}

    for indice, valor in enumerate(numeros):
        soma_acumulada += valor
        diferenca = soma_acumulada - alvo

        if diferenca in primeira_ocorrencia:
            comprimento = indice - primeira_ocorrencia[diferenca]
            if comprimento > maior_comprimento:
                maior_comprimento = comprimento

        if soma_acumulada not in primeira_ocorrencia:
            primeira_ocorrencia[soma_acumulada] = indice

    return maior_comprimento
