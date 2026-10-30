def resumir_intervalos(numeros: list[int]) -> str:
    """Resume inteiros únicos e ordenados em intervalos consecutivos.

    Sequências de dois ou mais números consecutivos viram ``inicio-fim``.
    Valores isolados aparecem sozinhos. Os trechos são unidos por ``", "``.
    A lista recebida não é modificada.
    """
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")

    for n in numeros:
        if type(n) is not int:
            raise TypeError("todos os elementos devem ser int")

    if not numeros:
        return ""

    unicos = sorted(set(numeros))
    partes: list[str] = []
    inicio = fim = unicos[0]

    for i in range(1, len(unicos)):
        n = unicos[i]
        if n == fim + 1:
            fim = n
            continue
        partes.append(str(inicio) if inicio == fim else f"{inicio}-{fim}")
        inicio = fim = n

    partes.append(str(inicio) if inicio == fim else f"{inicio}-{fim}")
    return ", ".join(partes)
