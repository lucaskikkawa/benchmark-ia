"""Fechamento de boletim conforme o contrato do enunciado."""

import math
from decimal import Decimal, ROUND_HALF_UP


def fechar_boletim(provas: list) -> dict:
    if not isinstance(provas, list):
        raise TypeError("provas deve ser list")
    if len(provas) == 0 or len(provas) > 4:
        raise ValueError("provas deve ter de 1 a 4 posicoes")

    notas = []
    for nota in provas:
        if nota is None:
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota invalida")
        if isinstance(nota, float) and not math.isfinite(nota):
            raise ValueError("nota nao finita")
        if nota < 0 or nota > 10:
            raise ValueError("nota fora de [0, 10]")
        notas.append(nota)

    if not notas:
        raise ValueError("nenhuma nota valida")

    descartada = None
    if len(notas) == 4:
        menor = min(notas)
        notas.remove(menor)  # remove só a primeira ocorrência
        descartada = float(menor)

    soma = sum((Decimal(str(n)) for n in notas), Decimal(0))
    media_dec = (soma / len(notas)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)

    if media_dec >= 9:
        conceito = "A"
    elif media_dec >= 7:
        conceito = "B"
    elif media_dec >= 5:
        conceito = "C"
    else:
        conceito = "D"

    return {
        "media": float(media_dec),
        "conceito": conceito,
        "aprovado": conceito != "D",
        "descartada": descartada,
    }
