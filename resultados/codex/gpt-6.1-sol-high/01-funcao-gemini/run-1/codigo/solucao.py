def _inteiro_para_texto(numero: int) -> str:
    """Converte também inteiros que excedem o limite decimal do Python."""
    try:
        return str(numero)
    except ValueError:
        # Não altera o limite global de conversão configurado pelo chamador.
        sinal = "-" if numero < 0 else ""
        numero = abs(numero)
        partes = []
        while numero:
            numero, resto = divmod(numero, 1_000_000_000)
            partes.append(resto)
        return sinal + str(partes[-1]) + "".join(
            f"{parte:09d}" for parte in reversed(partes[:-1])
        )


def resumir_intervalos(numeros: list[int]) -> str:
    """Ordena valores únicos e resume sequências consecutivas sem mutar a lista."""
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")
    if any(type(numero) is not int for numero in numeros):
        raise TypeError("todos os elementos devem ser inteiros primitivos")

    ordenados = sorted(set(numeros))
    if not ordenados:
        return ""

    intervalos = []
    inicio = fim = ordenados[0]
    for numero in ordenados[1:]:
        if numero == fim + 1:
            fim = numero
            continue
        intervalos.append(
            _inteiro_para_texto(inicio)
            if inicio == fim
            else f"{_inteiro_para_texto(inicio)}-{_inteiro_para_texto(fim)}"
        )
        inicio = fim = numero

    intervalos.append(
        _inteiro_para_texto(inicio)
        if inicio == fim
        else f"{_inteiro_para_texto(inicio)}-{_inteiro_para_texto(fim)}"
    )
    return ", ".join(intervalos)
