def resumir_intervalos(numeros: list[int]) -> str:
    """Resume valores inteiros únicos em intervalos consecutivos ordenados."""
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")
    if any(type(numero) is not int for numero in numeros):
        raise TypeError("todos os elementos devem ser inteiros primitivos")

    ordenados = sorted(set(numeros))
    if not ordenados:
        return ""

    partes = []
    inicio = fim = ordenados[0]
    for numero in ordenados[1:]:
        if numero == fim + 1:
            fim = numero
        else:
            partes.append(str(inicio) if inicio == fim else f"{inicio}-{fim}")
            inicio = fim = numero

    partes.append(str(inicio) if inicio == fim else f"{inicio}-{fim}")
    return ", ".join(partes)
