import re

_UNIT_INFO: dict[str, tuple[int, int]] = {
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
_INT_CHUNK_THRESHOLD = 500


def _parse_digits(digits: str) -> int:
    """Converte uma sequência de dígitos ASCII em int exato sem estourar o limite de str->int."""
    digits = digits.lstrip("0")
    if not digits:
        return 0
    if len(digits) <= _INT_CHUNK_THRESHOLD:
        return int(digits)

    pow10_cache: dict[int, int] = {}

    def _divide_and_conquer(chunk: str) -> int:
        n = len(chunk)
        if n <= _INT_CHUNK_THRESHOLD:
            return int(chunk)
        mid = n >> 1
        right_len = n - mid
        scale = pow10_cache.get(right_len)
        if scale is None:
            scale = 10**right_len
            pow10_cache[right_len] = scale
        return _divide_and_conquer(chunk[:mid]) * scale + _divide_and_conquer(chunk[mid:])

    return _divide_and_conquer(digits)


def parse_duracao(texto: str) -> int:
    """Converte uma string de duração humana (componentes w, d, h, m, s) em segundos."""
    if not isinstance(texto, str):
        raise TypeError(f"Esperado str, recebido {type(texto).__name__}")

    stripped = str.strip(texto)
    if not stripped:
        raise ValueError("Duração vazia")

    tokens = str.split(stripped, maxsplit=5)
    if len(tokens) > 5:
        raise ValueError("Excesso de componentes na duração")

    total = 0
    last_order = -1

    for token in tokens:
        pos = 0
        end = len(token)
        while pos < end:
            match = _COMPONENT_RE.match(token, pos)
            if match is None:
                raise ValueError("Formato inválido de duração")
            order, multiplier = _UNIT_INFO[match.group(2)]
            if order <= last_order:
                raise ValueError("Componentes fora de ordem ou repetidos")
            last_order = order
            total += _parse_digits(match.group(1)) * multiplier
            pos = match.end()

    return total
