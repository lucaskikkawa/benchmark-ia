import re
import sys

_UNIDADES = {
    "w": (0, 604800),
    "W": (0, 604800),
    "d": (1, 86400),
    "D": (1, 86400),
    "h": (2, 3600),
    "H": (2, 3600),
    "m": (3, 60),
    "M": (3, 60),
    "s": (4, 1),
    "S": (4, 1),
}

_TOKEN_RE = re.compile(r"\s*+([0-9]++)([wWdDhHmMsS])")


def _parse_int(num_str: str) -> int:
    if len(num_str) <= 600:
        return int(num_str)
    prev = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(0)
    try:
        return int(num_str)
    finally:
        sys.set_int_max_str_digits(prev)


def parse_duracao(texto: str) -> int:
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma string")

    n = len(texto)
    pos = 0
    ultima_ordem = -1
    total = 0
    encontrou = False

    while pos < n:
        m = _TOKEN_RE.match(texto, pos)
        if m is None:
            break
        encontrou = True
        num_str, unidade = m.group(1), m.group(2)
        ordem, fator = _UNIDADES[unidade]
        if ordem <= ultima_ordem:
            raise ValueError(f"Unidade fora de ordem ou repetida: {unidade!r}")
        ultima_ordem = ordem
        total += _parse_int(num_str) * fator
        pos = m.end()

    if not encontrou:
        raise ValueError("Duração vazia ou inválida")

    if pos < n and not texto[pos:].isspace():
        raise ValueError("Texto extra inválido no final da duração")

    return total
