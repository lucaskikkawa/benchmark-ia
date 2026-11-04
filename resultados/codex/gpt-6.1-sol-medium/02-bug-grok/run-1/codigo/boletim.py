"""Validação de notas e fechamento de boletim."""

from decimal import Decimal, ROUND_HALF_UP
from math import isfinite


def fechar_boletim(provas: list) -> dict:
    if not isinstance(provas, list):
        raise TypeError("provas deve ser list")
    if not 1 <= len(provas) <= 4:
        raise ValueError("provas deve conter de 1 a 4 posições")
    nums = []
    for nota in provas:
        if nota is None:
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota invalida")
        if not 0 <= nota <= 10 or not isfinite(nota):
            raise ValueError("nota invalida")
        nums.append(nota)
    if not nums:
        raise ValueError("é necessária pelo menos uma nota")

    descartada = None
    if len(nums) == 4:
        menor = min(nums)
        nums.remove(menor)
        descartada = float(menor)

    soma = sum((Decimal(str(nota)) for nota in nums), Decimal(0))
    media = (soma / len(nums)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
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
