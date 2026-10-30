def resumir_intervalos(numeros: list[int]) -> str:
    if not isinstance(numeros, list):
        raise TypeError("'numeros' deve ser uma lista")
    if any(type(x) is not int for x in numeros):
        raise TypeError("todos os elementos devem ser do tipo int primitivo")

    # sorted() cria uma nova lista, então a entrada do chamador não é alterada
    valores = sorted(set(numeros))
    if not valores:
        return ""

    partes = []
    inicio = anterior = valores[0]
    for atual in valores[1:]:
        if atual == anterior + 1:
            anterior = atual
            continue
        partes.append(_formatar(inicio, anterior))
        inicio = anterior = atual
    partes.append(_formatar(inicio, anterior))

    return ", ".join(partes)


def _formatar(inicio: int, fim: int) -> str:
    if inicio == fim:
        return str(inicio)
    return f"{inicio}-{fim}"
