"""Módulo para conversão de texto de duração em segundos."""

_UNIT_MULTIPLIERS = {
    'w': 604800,
    'd': 86400,
    'h': 3600,
    'm': 60,
    's': 1,
}

_UNIT_ORDER = {
    'w': 0,
    'd': 1,
    'h': 2,
    'm': 3,
    's': 4,
}


def _parse_digits(digits: str) -> int:
    """Converte string de dígitos ASCII em int sem limite de tamanho."""
    if len(digits) <= 4000:
        return int(digits)
    stripped = digits.lstrip('0')
    if not stripped:
        return 0
    if len(stripped) <= 4000:
        return int(stripped)
    val = 0
    for k in range(0, len(stripped), 4000):
        chunk = stripped[k:k + 4000]
        val = val * (10 ** len(chunk)) + int(chunk)
    return val


def parse_duracao(texto: str) -> int:
    """Converte uma duração escrita por humanos em segundos.

    Parâmetros:
        texto: Duração formada por 1 a 5 componentes <inteiro><unidade>
               na ordem w, d, h, m, s.

    Retorna:
        Total em segundos (int).

    Lança:
        TypeError: se texto não for str (ou subclasse).
        ValueError: se a entrada estiver fora do formato aceito.
    """
    if not isinstance(texto, str):
        raise TypeError(f"Esperado str, recebido {type(texto).__name__}")

    n = len(texto)
    i = 0

    # Ignora espaços em branco no início
    while i < n and texto[i].isspace():
        i += 1

    if i == n:
        raise ValueError("Texto vazio ou contendo apenas espaços.")

    total = 0
    last_order = -1

    while i < n:
        start_digits = i
        while i < n and '0' <= texto[i] <= '9':
            i += 1

        if i == start_digits:
            raise ValueError(f"Esperado dígito na posição {i}, encontrado {texto[i]!r}.")

        digits = texto[start_digits:i]

        if i == n:
            raise ValueError("Número sem unidade.")

        unit_char = texto[i].lower()
        if unit_char not in _UNIT_ORDER:
            raise ValueError(f"Unidade inválida: {texto[i]!r}.")

        order = _UNIT_ORDER[unit_char]
        if order <= last_order:
            raise ValueError(f"Unidade {texto[i]!r} fora de ordem ou repetida.")

        last_order = order
        i += 1

        val = _parse_digits(digits)
        total += val * _UNIT_MULTIPLIERS[unit_char]

        if i == n:
            break

        if '0' <= texto[i] <= '9':
            # Próximo componente colado imediatamente
            continue
        elif texto[i].isspace():
            while i < n and texto[i].isspace():
                i += 1
        else:
            raise ValueError(f"Caractere inválido após unidade: {texto[i]!r}.")

    return total
