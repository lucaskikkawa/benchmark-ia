def resumir_intervalos(numeros: list[int]) -> str:
    """Resume inteiros únicos em intervalos consecutivos, separados por vírgula."""
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")

    for valor in numeros:
        if type(valor) is not int:
            raise TypeError("todos os elementos devem ser do tipo int")

    if not numeros:
        return ""

    unicos = sorted(set(numeros))

    partes: list[str] = []
    inicio = anterior = unicos[0]

    for atual in unicos[1:]:
        if atual == anterior + 1:
            anterior = atual
            continue
        partes.append(str(inicio) if inicio == anterior else f"{inicio}-{anterior}")
        inicio = anterior = atual

    partes.append(str(inicio) if inicio == anterior else f"{inicio}-{anterior}")
    return ", ".join(partes)
