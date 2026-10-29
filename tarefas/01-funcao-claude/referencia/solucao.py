"""Conversão de durações escritas por humanos (ex.: "1h30m") em segundos."""

import re

# Unidades na ordem obrigatória em que podem aparecer.
SEGUNDOS_POR_UNIDADE = {"w": 604800, "d": 86400, "h": 3600, "m": 60, "s": 1}
_ORDEM = {unidade: posicao for posicao, unidade in enumerate(SEGUNDOS_POR_UNIDADE)}

# re.ASCII: só dígitos 0-9 e espaços ASCII; sem IGNORECASE (que aceitaria "ſ" como "s").
_ESPACOS = re.compile(r"\s*", re.ASCII)
_COMPONENTE = re.compile(r"([0-9]+)([A-Za-z])", re.ASCII)

# int(str) recusa strings com mais de ~4300 dígitos (Python 3.11+); converte em blocos.
_BLOCO = 1000


def _inteiro(digitos: str) -> int:
    valor = 0
    for inicio in range(0, len(digitos), _BLOCO):
        bloco = digitos[inicio:inicio + _BLOCO]
        valor = valor * 10 ** len(bloco) + int(bloco)
    return valor


def parse_duracao(texto: str) -> int:
    """Converte uma duração como "1w 2d 3h 4m 5s" em segundos.

    Varre a string uma única vez (tempo linear), componente a componente.

    Raises:
        TypeError: se ``texto`` não for ``str``.
        ValueError: se ``texto`` não seguir o formato especificado.
    """
    if not isinstance(texto, str):
        raise TypeError(f"esperado str, recebido {type(texto).__name__}")

    total = 0
    ultima_ordem = -1
    pos = _ESPACOS.match(texto).end()
    if pos == len(texto):
        raise ValueError(f"duração vazia: {texto!r}")
    while pos < len(texto):
        componente = _COMPONENTE.match(texto, pos)
        if componente is None:
            raise ValueError(f"duração inválida: {texto[:50]!r}")
        unidade = componente.group(2).lower()
        ordem = _ORDEM.get(unidade)
        if ordem is None:
            raise ValueError(f"unidade desconhecida {unidade!r} em {texto[:50]!r}")
        if ordem <= ultima_ordem:
            raise ValueError(f"unidade fora de ordem ou repetida {unidade!r} em {texto[:50]!r}")
        ultima_ordem = ordem
        total += _inteiro(componente.group(1)) * SEGUNDOS_POR_UNIDADE[unidade]
        pos = _ESPACOS.match(texto, componente.end()).end()
    return total
