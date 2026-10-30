import sys


def resumir_intervalos(numeros: list[int]) -> str:
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")
    for x in numeros:
        if type(x) is not int:
            raise TypeError("todos os elementos devem ser do tipo int")

    valores = sorted(set(numeros))
    if not valores:
        return ""

    partes = []
    inicio = fim = valores[0]
    for x in valores[1:]:
        if x == fim + 1:
            fim = x
        else:
            partes.append(_formatar(inicio, fim))
            inicio = fim = x
    partes.append(_formatar(inicio, fim))
    return ", ".join(partes)


def _para_str(n: int) -> str:
    try:
        return str(n)
    except ValueError:
        # Python 3.11+ limita a conversao de inteiros muito grandes para str.
        limite = sys.get_int_max_str_digits()
        sys.set_int_max_str_digits(0)
        try:
            return str(n)
        finally:
            sys.set_int_max_str_digits(limite)


def _formatar(inicio: int, fim: int) -> str:
    if inicio == fim:
        return _para_str(inicio)
    return f"{_para_str(inicio)}-{_para_str(fim)}"
