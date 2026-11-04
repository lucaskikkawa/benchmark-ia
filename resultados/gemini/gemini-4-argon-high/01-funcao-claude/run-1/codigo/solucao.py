import re

_WS_RE = re.compile(r"\s*+")
_COMP_RE = re.compile(r"([0-9]++)([wdhmsWDHMS])\s*+")

_UNIDADES: dict[str, tuple[int, int]] = {
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


def _str_para_int(s: str) -> int:
    s = s.lstrip("0")
    if not s:
        return 0
    if len(s) <= 640:
        return int(s)
    meio = len(s) >> 1
    return _str_para_int(s[:meio]) * (10 ** (len(s) - meio)) + _str_para_int(s[meio:])


def parse_duracao(texto: str) -> int:
    if not isinstance(texto, str):
        raise TypeError("O argumento 'texto' deve ser do tipo str.")
    if type(texto) is not str:
        texto = str.__str__(texto)

    n = len(texto)
    pos = _WS_RE.match(texto).end()
    if pos == n:
        raise ValueError("A duração não pode ser vazia.")

    ultima_ordem = -1
    componentes: list[tuple[str, int]] = []

    while pos < n:
        m = _COMP_RE.match(texto, pos)
        if m is None:
            raise ValueError(f"Formato de duração inválido na posição {pos}.")
        num_str, unidade = m.group(1), m.group(2)
        ordem, fator = _UNIDADES[unidade]
        if ordem <= ultima_ordem:
            raise ValueError(f"Unidade fora de ordem ou repetida: {unidade!r}.")
        ultima_ordem = ordem
        componentes.append((num_str, fator))
        pos = m.end()

    total = 0
    for num_str, fator in componentes:
        total += _str_para_int(num_str) * fator
    return total
