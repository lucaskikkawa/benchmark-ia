def resumir_intervalos(numeros: list[int]) -> str:
    """Resume inteiros únicos, em ordem crescente, como intervalos consecutivos.

    Dois ou mais valores consecutivos viram ``inicio-fim``. Valores isolados
    permanecem sozinhos. As partes são unidas por ``", "``. Lista vazia
    devolve ``""``. A lista recebida não é modificada.
    """
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")

    unicos: set[int] = set()
    adicionar = unicos.add
    for n in numeros:
        # bool é subclasse de int; só o tipo primitivo int é aceito.
        if type(n) is not int:
            raise TypeError(
                "todos os elementos devem ser int primitivo "
                "(bool e subclasses de int não são permitidos)"
            )
        adicionar(n)

    if not unicos:
        return ""

    ordenados = iter(sorted(unicos))
    partes: list[str] = []
    inicio = fim = next(ordenados)
    for n in ordenados:
        if n == fim + 1:
            fim = n
            continue
        partes.append(f"{inicio}-{fim}" if inicio != fim else str(inicio))
        inicio = fim = n
    partes.append(f"{inicio}-{fim}" if inicio != fim else str(inicio))
    return ", ".join(partes)
