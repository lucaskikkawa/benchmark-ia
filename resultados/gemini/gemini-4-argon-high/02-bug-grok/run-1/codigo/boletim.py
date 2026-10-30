"""Fechamento de boletim."""

from decimal import Decimal, ROUND_HALF_UP
import math


def fechar_boletim(provas: list) -> dict:
    if not isinstance(provas, list):
        raise TypeError("provas deve ser list")
    if len(provas) == 0 or len(provas) > 4:
        raise ValueError("quantidade de provas invalida")

    validas = []
    for nota in provas:
        if nota is None:
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota invalida")
        if not math.isfinite(nota) or nota < 0 or nota > 10:
            raise ValueError("nota fora do intervalo [0, 10]")
        validas.append(nota)

    if not validas:
        raise ValueError("nenhuma nota valida")

    descartada = None
    if len(validas) == 4:
        menor = min(validas)
        validas.remove(menor)
        descartada = float(menor) + 0.0

    soma = sum((Decimal(str(nota)) for nota in validas), Decimal(0))
    media_dec = (soma / len(validas)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    media = float(media_dec) + 0.0

    if media_dec >= 9:
        conceito = "A"
    elif media_dec >= 7:
        conceito = "B"
    elif media_dec >= 5:
        conceito = "C"
    else:
        conceito = "D"

    return {
        "media": media,
        "conceito": conceito,
        "aprovado": conceito != "D",
        "descartada": descartada,
    }
