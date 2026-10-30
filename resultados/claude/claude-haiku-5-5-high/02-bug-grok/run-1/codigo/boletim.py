"""Fechamento de boletim."""

import math
from decimal import ROUND_HALF_UP, Decimal


def fechar_boletim(provas):
    if not isinstance(provas, list):
        raise TypeError("provas deve ser list")
    if not 1 <= len(provas) <= 4:
        raise ValueError("provas deve ter de 1 a 4 itens")

    notas = []
    for nota in provas:
        if nota is None:
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota invalida")
        if isinstance(nota, float) and not math.isfinite(nota):
            raise ValueError("nota invalida")
        if not 0 <= nota <= 10:
            raise ValueError("nota invalida")
        notas.append(nota)

    if not notas:
        raise ValueError("nenhuma nota valida")

    descartada = None
    if len(notas) == 4:
        menor = min(notas)
        notas.remove(menor)
        descartada = float(menor)

    soma = sum((Decimal(str(nota)) for nota in notas), Decimal(0))
    media = (soma / len(notas)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if media >= 9:
        conceito = "A"
    elif media >= 7:
        conceito = "B"
    elif media >= 5:
        conceito = "C"
    else:
        conceito = "D"

    return {
        "media": float(media),
        "conceito": conceito,
        "aprovado": conceito != "D",
        "descartada": descartada,
    }
