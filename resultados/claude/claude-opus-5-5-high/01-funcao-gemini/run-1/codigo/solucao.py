import sys


def resumir_intervalos(numeros: list[int]) -> str:
    """Resume uma lista de inteiros em intervalos consecutivos.

    Exemplo: [1, 2, 3, 5, 7, 8, 9] -> "1-3, 5, 7-9"
    """
    if not isinstance(numeros, list):
        raise TypeError("numeros deve ser uma lista")
    for x in numeros:
        if type(x) is not int:
            raise TypeError(f"elemento inválido: {x!r} (esperado int)")

    valores = sorted(set(numeros))
    if not valores:
        return ""

    partes = []
    inicio = anterior = valores[0]
    for x in valores[1:]:
        if x == anterior + 1:
            anterior = x
            continue
        partes.append(_formatar(inicio, anterior))
        inicio = anterior = x
    partes.append(_formatar(inicio, anterior))
    return ", ".join(partes)


def _int_para_str(n: int) -> str:
    try:
        return str(n)
    except ValueError:
        # Python 3.11+ limita a conversão de inteiros muito grandes para str;
        # remove o limite temporariamente para suportar magnitude arbitrária.
        limite = sys.get_int_max_str_digits()
        sys.set_int_max_str_digits(0)
        try:
            return str(n)
        finally:
            sys.set_int_max_str_digits(limite)


def _formatar(inicio: int, fim: int) -> str:
    if inicio == fim:
        return _int_para_str(inicio)
    return f"{_int_para_str(inicio)}-{_int_para_str(fim)}"
