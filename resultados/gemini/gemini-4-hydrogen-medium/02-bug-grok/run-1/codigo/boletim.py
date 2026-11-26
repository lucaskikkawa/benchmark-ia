"""Fechamento de boletim conforme o contrato do enunciado."""

from decimal import Decimal, ROUND_HALF_UP
import math


def fechar_boletim(provas: list) -> dict:
    if not isinstance(provas, list):
        raise TypeError("provas deve ser list")
    if len(provas) == 0 or len(provas) > 4:
        raise ValueError("provas deve ter entre 1 e 4 posicoes")

    validas = []
    for nota in provas:
        if nota is None:
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota deve ser int, float ou None")
        if not math.isfinite(nota) or nota < 0 or nota > 10:
            raise ValueError("nota deve ser finita e estar em [0, 10]")
        validas.append(nota)

    if not validas:
        raise ValueError("deve haver pelo menos uma nota valida")

    descartada = None
    if len(validas) == 4:
        idx_menor = min(range(len(validas)), key=lambda i: validas[i])
        descartada = float(validas.pop(idx_menor))

    decimais = [Decimal(str(nota)) for nota in validas]
    soma = sum(decimais, Decimal("0"))
    media_dec = (soma / len(decimais)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    media = float(media_dec)
    if media == 0:
        media = 0.0

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
