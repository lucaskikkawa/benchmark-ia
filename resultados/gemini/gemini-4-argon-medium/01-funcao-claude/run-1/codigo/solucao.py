import re
import sys

_TOKEN_RE = re.compile(r"[0-9]+[wWdDhHmMsS]")

_UNIDADES = {
    "w": (0, 604800),
    "d": (1, 86400),
    "h": (2, 3600),
    "m": (3, 60),
    "s": (4, 1),
}


def _str_to_int(num_str: str) -> int:
    if len(num_str) <= 640:
        return int(num_str)
    limite_anterior = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(0)
    try:
        return int(num_str)
    finally:
        sys.set_int_max_str_digits(limite_anterior)


def parse_duracao(texto: str) -> int:
    if not isinstance(texto, str):
        raise TypeError("A entrada deve ser uma string (str).")

    partes = str(texto).split()
    if not partes:
        raise ValueError("Duração vazia.")

    total = 0
    ultima_ordem = -1

    for parte in partes:
        pos = 0
        tam = len(parte)
        while pos < tam:
            m = _TOKEN_RE.match(parte, pos)
            if m is None:
                raise ValueError("Formato de duração inválido.")
            pos = m.end()
            token = m.group(0)
            unidade = token[-1].lower()
            ordem, multiplicador = _UNIDADES[unidade]
            if ordem <= ultima_ordem:
                raise ValueError("Ordem ou repetição inválida de unidade.")
            ultima_ordem = ordem
            total += _str_to_int(token[:-1]) * multiplicador

    return total
