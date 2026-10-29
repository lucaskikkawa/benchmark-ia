"""Conversão de durações com unidades de dias, horas, minutos e segundos."""

import re


_FORMATO = re.compile(
    r"(?:([0-9]+)[dD]\s*)?"
    r"(?:([0-9]+)[hH]\s*)?"
    r"(?:([0-9]+)[mM]\s*)?"
    r"(?:([0-9]+)[sS]\s*)?"
)


def parse_duracao(texto: str) -> int:
    """Retorna a duração em segundos, validando integralmente o formato."""
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma string")

    resultado = _FORMATO.fullmatch(texto.strip())
    if resultado is None or not any(resultado.groups()):
        raise ValueError("formato de duração inválido")

    total = 0
    for digitos, fator in zip(resultado.groups(), (86400, 3600, 60, 1)):
        if digitos is not None:
            # Blocos evitam o limite de conversão de strings longas do Python.
            valor = 0
            for inicio in range(0, len(digitos), 1000):
                bloco = digitos[inicio:inicio + 1000]
                valor = valor * 10 ** len(bloco) + int(bloco)
            total += valor * fator
    return total
