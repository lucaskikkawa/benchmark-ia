import re
import sys

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
_MAX_CHUNK_DIGITS = 1000


def _parse_ascii_int(digits: str) -> int:
    digits = digits.lstrip("0")
    if not digits:
        return 0

    limit = sys.get_int_max_str_digits()
    chunk = _MAX_CHUNK_DIGITS if limit == 0 else min(limit, _MAX_CHUNK_DIGITS)
    n = len(digits)
    if n <= chunk:
        return int(digits)

    chunks = [int(digits[max(0, i - chunk):i]) for i in range(n, 0, -chunk)]
    base = 10**chunk
    while len(chunks) > 1:
        merged: list[int] = []
        for i in range(0, len(chunks), 2):
            if i + 1 < len(chunks):
                merged.append(chunks[i] + chunks[i + 1] * base)
            else:
                merged.append(chunks[i])
        chunks = merged
        if len(chunks) > 1:
            base *= base
    return chunks[0]


def parse_duracao(texto: str) -> int:
    if not isinstance(texto, str):
        raise TypeError(f"esperado str, recebido {type(texto).__name__}")

    tokens = str.split(texto, None, 5)
    if not tokens or len(tokens) > 5:
        raise ValueError("duração inválida")

    total = 0
    last_order = -1
    for token in tokens:
        pos = 0
        end = len(token)
        while pos < end:
            match = _COMPONENT_RE.match(token, pos)
            if match is None:
                raise ValueError("duração inválida")
            order, multiplier = _UNITS[match.group(2)]
            if order <= last_order:
                raise ValueError("duração inválida")
            last_order = order
            total += _parse_ascii_int(match.group(1)) * multiplier
            pos = match.end()

    return total
