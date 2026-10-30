def resumir_intervalos(numeros: list[int]) -> str:
    """Resume inteiros únicos em ordem crescente, agrupando consecutivos."""
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")

    if any(type(numero) is not int for numero in numeros):
        raise TypeError("todos os elementos devem ser inteiros primitivos")

    ordenados = sorted(set(numeros))
    if not ordenados:
        return ""

    partes: list[str] = []
    inicio = anterior = ordenados[0]

    for numero in ordenados[1:]:
        if numero == anterior + 1:
            anterior = numero
            continue

        if inicio == anterior:
            partes.append(str(inicio))
        else:
            partes.append(f"{inicio}-{anterior}")
        inicio = anterior = numero

    if inicio == anterior:
        partes.append(str(inicio))
    else:
        partes.append(f"{inicio}-{anterior}")

    return ", ".join(partes)
