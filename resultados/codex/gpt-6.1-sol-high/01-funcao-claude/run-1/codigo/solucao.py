"""Conversão de durações com unidades de semanas a segundos."""

import re


_COMPONENTE = re.compile(r"([0-9]+)([wWdDhHmMsS])")
_ESPACOS = re.compile(r"\s*")
_UNIDADES = {"w": (0, 604800), "d": (1, 86400), "h": (2, 3600),
             "m": (3, 60), "s": (4, 1)}


def _inteiro_decimal(digitos: str) -> int:
    # Blocos pequenos evitam o limite de conversão decimal do Python 3.11,
    # sem modificar configurações globais do interpretador.
    valor = 0
    for inicio in range(0, len(digitos), 18):
        bloco = digitos[inicio:inicio + 18]
        valor = valor * (10 ** len(bloco)) + int(bloco)
    return valor


def parse_duracao(texto: str) -> int:
    """Retorna os segundos de uma duração; rejeita formatos inválidos."""
    if not isinstance(texto, str):
        raise TypeError("texto deve ser str")

    posicao = 0
    ultima_ordem = -1
    componentes = []
    while True:
        posicao = _ESPACOS.match(texto, posicao).end()
        if posicao == len(texto):
            break

        componente = _COMPONENTE.match(texto, posicao)
        if componente is None:
            raise ValueError("duração inválida")

        digitos, unidade = componente.groups()
        ordem, fator = _UNIDADES[unidade.lower()]
        if ordem <= ultima_ordem:
            raise ValueError("unidades repetidas ou fora de ordem")
        ultima_ordem = ordem
        componentes.append((digitos, fator))
        posicao = componente.end()

    if not componentes:
        raise ValueError("duração vazia")

    return sum(_inteiro_decimal(digitos) * fator
               for digitos, fator in componentes)
