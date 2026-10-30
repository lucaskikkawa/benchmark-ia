"""Conversão de durações humanas para segundos."""

import re


_COMPONENTE = re.compile(r"([0-9]+)([wWdDhHmMsS])")
_ESPACOS = re.compile(r"\s*")
_UNIDADES = {
    "w": (0, 604800),
    "d": (1, 86400),
    "h": (2, 3600),
    "m": (3, 60),
    "s": (4, 1),
}


def _inteiro_ascii(digitos: str) -> int:
    # Blocos pequenos evitam o limite de dígitos de int(str) no Python 3.11,
    # sem alterar configurações globais do interpretador.
    valor = 0
    for inicio in range(0, len(digitos), 9):
        bloco = digitos[inicio:inicio + 9]
        valor = valor * (10 ** len(bloco)) + int(bloco)
    return valor


def parse_duracao(texto: str) -> int:
    """Retorna os segundos; rejeita tipos e formatos fora da especificação."""
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma string")

    posicao = 0
    ultima_ordem = -1
    total = 0
    tamanho = len(texto)

    while True:
        # Cada trecho de espaços é percorrido uma única vez, inclusive quando
        # há texto inválido depois dele.
        posicao = _ESPACOS.match(texto, posicao).end()
        if posicao == tamanho:
            if ultima_ordem == -1:
                raise ValueError("duração vazia")
            return total

        componente = _COMPONENTE.match(texto, posicao)
        if componente is None:
            raise ValueError("componente de duração inválido")

        digitos, unidade = componente.groups()
        ordem, fator = _UNIDADES[unidade.lower()]
        if ordem <= ultima_ordem:
            raise ValueError("unidade repetida ou fora de ordem")

        total += _inteiro_ascii(digitos) * fator
        ultima_ordem = ordem
        posicao = componente.end()
