"""Módulo para conversão de texto de duração em segundos."""

import re

_UNIT_INDEX = {
    'w': 0, 'W': 0,
    'd': 1, 'D': 1,
    'h': 2, 'H': 2,
    'm': 3, 'M': 3,
    's': 4, 'S': 4,
}

_UNIT_SECONDS = {
    'w': 604800, 'W': 604800,
    'd': 86400,  'D': 86400,
    'h': 3600,   'H': 3600,
    'm': 60,     'M': 60,
    's': 1,      'S': 1,
}

_WS_PATTERN = re.compile(r'\s*+')
_COMP_PATTERN = re.compile(r'([0-9]++)([wdhmsWDHMS])')


def _str_to_int(s: str) -> int:
    """Converte string de dígitos decimais em inteiro sem limite de dígitos."""
    s = s.lstrip('0')
    if not s:
        return 0
    n = len(s)
    if n <= 640:
        return int(s)
    mid = n // 2
    return _str_to_int(s[:mid]) * (10 ** (n - mid)) + _str_to_int(s[mid:])


def parse_duracao(texto: str) -> int:
    """
    Recebe uma duração escrita em texto e retorna o total em segundos (int).

    Formato aceito:
    - 1 a 5 componentes <inteiro><unidade>
    - Unidades: w (semanas), d (dias), h (horas), m (minutos), s (segundos)
    - Ordem estrita: w, d, h, m, s (cada unidade no máximo uma vez)
    - Componentes colados ou separados por espaços em branco
    - Espaços em branco no início/fim ignorados
    - Sem espaço entre número e unidade
    """
    if not isinstance(texto, str):
        raise TypeError(f"texto deve ser uma string, recebido: {type(texto).__name__}")

    n = len(texto)
    pos = _WS_PATTERN.match(texto, 0).end()
    if pos == n:
        raise ValueError("Texto vazio ou composto apenas por espaços")

    last_unit_idx = -1
    total_seconds = 0

    while pos < n:
        m = _COMP_PATTERN.match(texto, pos)
        if m is None:
            raise ValueError(f"Componente inválido na posição {pos}: {texto[pos:pos+20]!r}")

        digits = m.group(1)
        unit = m.group(2)
        unit_idx = _UNIT_INDEX[unit]

        if unit_idx <= last_unit_idx:
            raise ValueError(
                f"Unidade '{unit}' fora de ordem ou repetida (posição {pos})"
            )
        last_unit_idx = unit_idx

        val = _str_to_int(digits)
        total_seconds += val * _UNIT_SECONDS[unit]

        pos = m.end()
        pos = _WS_PATTERN.match(texto, pos).end()

    return total_seconds
