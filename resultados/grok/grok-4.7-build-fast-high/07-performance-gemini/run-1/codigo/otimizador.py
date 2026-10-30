"""Maior subarray contíguo cuja soma é exatamente o alvo."""


def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    """Retorna o comprimento máximo de um subarray contíguo com soma `alvo`.

    Se nenhum subarray somar `alvo`, ou se a lista for vazia, retorna 0.
    `numeros` precisa ser `list` e cada elemento, assim como `alvo`, precisa
    ser um `int` primitivo (`bool` é rejeitado).
    """
    if type(numeros) is not list:
        raise TypeError("numeros deve ser list")
    if type(alvo) is not int:
        raise TypeError("alvo deve ser int")

    # prefixo -> índice mais à esquerda em que essa soma prefixada ocorreu.
    # O prefixo 0 existe antes do primeiro elemento (índice -1).
    primeiro = {0: -1}
    buscar = primeiro.get
    prefixo = 0
    melhor = 0
    indice = 0
    tipo_int = int

    for valor in numeros:
        if type(valor) is not tipo_int:
            raise TypeError("cada elemento de numeros deve ser int")
        prefixo += valor
        inicio = buscar(prefixo - alvo)
        if inicio is not None:
            tamanho = indice - inicio
            if tamanho > melhor:
                melhor = tamanho
        # Guarda só a primeira ocorrência: ela produz o subarray mais longo.
        if prefixo not in primeiro:
            primeiro[prefixo] = indice
        indice += 1

    return melhor
