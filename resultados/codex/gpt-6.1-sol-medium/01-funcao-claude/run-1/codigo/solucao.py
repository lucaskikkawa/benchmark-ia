"""Conversão de durações com unidades d, h, m e s para segundos."""

import re


_COMPONENTE = re.compile(r"([0-9]+)([dDhHmMsS])\s*")
_UNIDADES = {"d": (0, 86400), "h": (1, 3600), "m": (2, 60), "s": (3, 1)}


def parse_duracao(texto: str) -> int:
    """Retorna os segundos; rejeita componentes inválidos ou fora de ordem."""
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma string")

    texto = texto.strip()
    if not texto:
        raise ValueError("duração vazia")

    total = 0
    posicao = 0
    ordem_anterior = -1
    while posicao < len(texto):
        componente = _COMPONENTE.match(texto, posicao)
        if componente is None:
            raise ValueError("formato de duração inválido")

        digitos, unidade = componente.groups()
        ordem, fator = _UNIDADES[unidade.lower()]
        if ordem <= ordem_anterior:
            raise ValueError("unidades repetidas ou fora de ordem")

        # Blocos pequenos evitam o limite de conversão de strings do Python
        # 3.11, mantendo componentes sem limite de quantidade de dígitos.
        valor = 0
        for inicio in range(0, len(digitos), 9):
            bloco = digitos[inicio:inicio + 9]
            valor = valor * 10 ** len(bloco) + int(bloco)

        total += valor * fator
        ordem_anterior = ordem
        posicao = componente.end()

    return total
