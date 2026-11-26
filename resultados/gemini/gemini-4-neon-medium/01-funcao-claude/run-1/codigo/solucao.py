from __future__ import annotations

import re

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

_COMPONENT_RE = re.compile(r"([0-9]++)([wWdDhHmMsS])")
_INT_CHUNK_LIMIT = 600


def _parse_large_int(digits: str) -> int:
    if len(digits) <= _INT_CHUNK_LIMIT:
        return int(digits)
    mid = len(digits) // 2
    return _parse_large_int(digits[:mid]) * (10 ** (len(digits) - mid)) + _parse_large_int(
        digits[mid:]
    )


def _parse_int(digits: str) -> int:
    if len(digits) <= _INT_CHUNK_LIMIT:
        return int(digits)
    stripped = digits.lstrip("0")
    if not stripped:
        return 0
    return _parse_large_int(stripped)


def parse_duracao(texto: str) -> int:
    if not isinstance(texto, str):
        raise TypeError(f"esperado str, recebido {type(texto).__name__}")

    tokens = str.split(texto, None, 5)
    if not tokens or len(tokens) > 5:
        raise ValueError("duração inválida")

    total = 0
    last_rank = -1

    for token in tokens:
        pos = 0
        end = len(token)
        while pos < end:
            match = _COMPONENT_RE.match(token, pos)
            if match is None:
                raise ValueError("duração inválida")
            digits, unit = match.group(1), match.group(2)
            rank, multiplier = _UNITS[unit]
            if rank <= last_rank:
                raise ValueError("duração inválida")
            last_rank = rank
            total += _parse_int(digits) * multiplier
            pos = match.end()

    return total
