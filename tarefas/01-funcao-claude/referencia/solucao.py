"""Conversão de durações escritas por humanos (ex.: "1h30m") em segundos."""

import re

SEGUNDOS_POR_UNIDADE = {"d": 86400, "h": 3600, "m": 60, "s": 1}

# Cada unidade é opcional, aparece no máximo uma vez e na ordem d, h, m, s.
_PADRAO = re.compile(
    r"\s*"
    r"(?:(?P<d>[0-9]+)d)?\s*"
    r"(?:(?P<h>[0-9]+)h)?\s*"
    r"(?:(?P<m>[0-9]+)m)?\s*"
    r"(?:(?P<s>[0-9]+)s)?\s*",
    re.IGNORECASE,
)


def parse_duracao(texto: str) -> int:
    """Converte uma duração como "2d 3h 4m 5s" em segundos.

    Raises:
        TypeError: se ``texto`` não for ``str``.
        ValueError: se ``texto`` não seguir o formato especificado.
    """
    if not isinstance(texto, str):
        raise TypeError(f"esperado str, recebido {type(texto).__name__}")

    correspondencia = _PADRAO.fullmatch(texto)
    if correspondencia is None:
        raise ValueError(f"duração inválida: {texto!r}")

    componentes = {u: v for u, v in correspondencia.groupdict().items() if v is not None}
    if not componentes:
        raise ValueError(f"duração vazia: {texto!r}")

    return sum(int(valor) * SEGUNDOS_POR_UNIDADE[unidade] for unidade, valor in componentes.items())
