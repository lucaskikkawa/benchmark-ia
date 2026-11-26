"""Fechamento de boletim conforme contrato do enunciado."""

from decimal import Decimal, ROUND_HALF_UP
import math


def fechar_boletim(provas: list) -> dict:
    if not isinstance(provas, list):
        raise TypeError("provas deve ser list")
    if len(provas) == 0 or len(provas) > 4:
        raise ValueError("provas deve ter entre 1 e 4 posicoes")

    notas = []
    for nota in provas:
        if nota is None:
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota deve ser int, float ou None")
        if isinstance(nota, float) and not math.isfinite(nota):
            raise ValueError("nota deve ser finita")
        if nota < 0 or nota > 10:
            raise ValueError("nota deve estar no intervalo [0, 10]")
        notas.append(nota)

    if not notas:
        raise ValueError("nenhuma nota valida")

    descartada = None
    if len(notas) == 4:
        idx_menor = min(range(len(notas)), key=lambda i: notas[i])
        descartada = float(notas.pop(idx_menor)) + 0.0

    decimais = [Decimal(str(nota)) for nota in notas]
    soma = sum(decimais, Decimal("0"))
    media_dec = (soma / len(decimais)).quantize(
        Decimal("0.01"), rounding=ROUND_HALF_UP
    )
    media = float(media_dec) + 0.0

    if media_dec >= Decimal("9"):
        conceito = "A"
    elif media_dec >= Decimal("7"):
        conceito = "B"
    elif media_dec >= Decimal("5"):
        conceito = "C"
    else:
        conceito = "D"

    return {
        "media": media,
        "conceito": conceito,
        "aprovado": conceito != "D",
        "descartada": descartada,
    }
