"""Fechamento de boletim."""

from decimal import Decimal, ROUND_HALF_UP
import math


def fechar_boletim(provas: list) -> dict:
    if not isinstance(provas, list):
        raise TypeError("provas deve ser list")
    if not 1 <= len(provas) <= 4:
        raise ValueError("provas deve conter de 1 a 4 itens")

    notas = []
    for nota in provas:
        if nota is None:
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota deve ser int, float ou None")
        if isinstance(nota, float) and not math.isfinite(nota):
            raise ValueError("nota deve ser finita")
        if nota < 0 or nota > 10:
            raise ValueError("nota deve estar entre 0 e 10")
        notas.append(nota)

    if not notas:
        raise ValueError("é necessária ao menos uma nota")

    descartada = None
    if len(notas) == 4:
        menor = min(notas)
        notas.remove(menor)
        descartada = float(menor)

    decimais = [Decimal(str(nota)) for nota in notas]
    media_decimal = (sum(decimais) / len(decimais)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    media = float(media_decimal)

    if media >= 9:
        conceito = "A"
    elif media >= 7:
        conceito = "B"
    elif media >= 5:
        conceito = "C"
    else:
        conceito = "D"

    return {
        "media": media,
        "conceito": conceito,
        "aprovado": conceito != "D",
        "descartada": descartada,
    }
