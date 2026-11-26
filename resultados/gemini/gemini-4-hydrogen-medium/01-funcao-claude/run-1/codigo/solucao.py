import re

_COMP_RE = re.compile(r"([0-9]+)([wWdDhHmMsS])")

_UNITS: dict[str, tuple[int, int]] = {
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

_CHUNK_SIZE = 4000
_CHUNK_BASE = 10**_CHUNK_SIZE


def _parse_ascii_int(digits: str) -> int:
    digits = digits.lstrip("0")
    if not digits:
        return 0
    if len(digits) <= _CHUNK_SIZE:
        return int(digits)

    val = 0
    i = 0
    n = len(digits)
    while i + _CHUNK_SIZE <= n:
        val = val * _CHUNK_BASE + int(digits[i : i + _CHUNK_SIZE])
        i += _CHUNK_SIZE
    if i < n:
        rem = n - i
        val = val * (10**rem) + int(digits[i:])
    return val


def parse_duracao(texto: str) -> int:
    """Converte uma string de duração humana (w, d, h, m, s) em segundos."""
    if not isinstance(texto, str):
        raise TypeError(f"Esperado str, recebido {type(texto).__name__}")

    tokens = str.split(texto, None, 6)
    if not tokens or len(tokens) > 5:
        raise ValueError("Duração inválida")

    total = 0
    last_unit_idx = -1

    for token in tokens:
        pos = 0
        n = len(token)
        while pos < n:
            match = _COMP_RE.match(token, pos)
            if match is None:
                raise ValueError(f"Formato inválido em {token!r}")

            digits, unit = match.group(1), match.group(2)
            unit_idx, mult = _UNITS[unit]
            if unit_idx <= last_unit_idx:
                raise ValueError(f"Unidade fora de ordem ou repetida: {unit!r}")

            last_unit_idx = unit_idx
            total += _parse_ascii_int(digits) * mult
            pos = match.end()

    if last_unit_idx == -1:
        raise ValueError("Duração vazia")

    return total
