"""Fechamento de boletim."""

import math
from decimal import Decimal, ROUND_HALF_UP


def fechar_boletim(provas: list) -> dict:
    if not isinstance(provas, list):
        raise TypeError("provas deve ser list")
    if not 1 <= len(provas) <= 4:
        raise ValueError("provas deve ter de 1 a 4 posicoes")

    notas = []
    for nota in provas:
        if nota is None:
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota invalida")
        if not math.isfinite(nota) or not 0 <= nota <= 10:
            raise ValueError("nota invalida")
        notas.append(nota)

    if not notas:
        raise ValueError("nenhuma nota valida")

    descartada = None
    if len(notas) == 4:
        menor = min(notas)
        notas.remove(menor)
        descartada = float(menor)

    n = len(notas)
    soma = sum(Decimal(str(nota)) for nota in notas)
    media = (soma / n).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

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
