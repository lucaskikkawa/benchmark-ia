def resumir_intervalos(numeros: list[int]) -> str:
    """Resume uma lista de números inteiros em intervalos consecutivos."""
    if not isinstance(numeros, list):
        raise TypeError("A entrada deve ser uma lista de inteiros.")

    for item in numeros:
        if type(item) is not int:
            raise TypeError(f"Item inválido: {item!r}. Esperado int.")

    if not numeros:
        return ""

    ordenados = sorted(set(numeros))
    intervalos: list[str] = []
    inicio = ordenados[0]
    anterior = ordenados[0]

    for n in ordenados[1:]:
        if n == anterior + 1:
            anterior = n
        else:
            if inicio == anterior:
                intervalos.append(str(inicio))
            else:
                intervalos.append(f"{inicio}-{anterior}")
            inicio = n
            anterior = n

    if inicio == anterior:
        intervalos.append(str(inicio))
    else:
        intervalos.append(f"{inicio}-{anterior}")

    return ", ".join(intervalos)
