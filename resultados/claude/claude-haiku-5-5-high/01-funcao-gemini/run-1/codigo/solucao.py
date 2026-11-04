def _formatar_intervalo(inicio: int, fim: int) -> str:
    if inicio == fim:
        return str(inicio)
    return f"{inicio}-{fim}"


def resumir_intervalos(numeros: list[int]) -> str:
    if not isinstance(numeros, list):
        raise TypeError("'numeros' deve ser uma lista")
    for x in numeros:
        if type(x) is not int:
            raise TypeError(f"elemento {x!r} não é um int primitivo")

    # set() remove duplicados sem alterar a lista original; sorted() devolve uma nova lista.
    valores = sorted(set(numeros))
    if not valores:
        return ""

    partes = []
    inicio = anterior = valores[0]
    for atual in valores[1:]:
        if atual == anterior + 1:
            anterior = atual
            continue
        partes.append(_formatar_intervalo(inicio, anterior))
        inicio = anterior = atual
    partes.append(_formatar_intervalo(inicio, anterior))

    return ", ".join(partes)
