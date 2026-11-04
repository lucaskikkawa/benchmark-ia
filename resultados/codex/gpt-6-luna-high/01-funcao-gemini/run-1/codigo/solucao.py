def resumir_intervalos(numeros: list[int]) -> str:
    """Resume números inteiros distintos em intervalos consecutivos."""
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")

    if any(type(numero) is not int for numero in numeros):
        raise TypeError("todos os elementos devem ser inteiros primitivos")

    ordenados = sorted(set(numeros))
    if not ordenados:
        return ""

    partes: list[str] = []
    inicio = fim = ordenados[0]

    for numero in ordenados[1:]:
        if numero == fim + 1:
            fim = numero
            continue

        partes.append(str(inicio) if inicio == fim else f"{inicio}-{fim}")
        inicio = fim = numero

    partes.append(str(inicio) if inicio == fim else f"{inicio}-{fim}")
    return ", ".join(partes)
