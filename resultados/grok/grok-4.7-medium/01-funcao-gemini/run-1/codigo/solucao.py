def resumir_intervalos(numeros: list[int]) -> str:
    """Agrupa inteiros únicos em intervalos consecutivos, no formato "a-b, c"."""
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")

    for valor in numeros:
        if type(valor) is not int:
            raise TypeError("todos os elementos devem ser do tipo int")

    unicos = sorted(set(numeros))
    if not unicos:
        return ""

    partes: list[str] = []
    inicio = fim = unicos[0]
    for numero in unicos[1:]:
        if numero == fim + 1:
            fim = numero
            continue
        partes.append(str(inicio) if inicio == fim else f"{inicio}-{fim}")
        inicio = fim = numero

    partes.append(str(inicio) if inicio == fim else f"{inicio}-{fim}")
    return ", ".join(partes)
