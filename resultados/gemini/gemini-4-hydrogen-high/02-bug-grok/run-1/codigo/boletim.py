"""Fechamento de boletim escolar conforme contrato."""

from decimal import Decimal, ROUND_HALF_UP
import math


def fechar_boletim(provas: list) -> dict:
    """Calcula média, conceito, aprovação e nota descartada a partir de uma lista de provas."""
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
        if (isinstance(nota, float) and not math.isfinite(nota)) or nota < 0 or nota > 10:
            raise ValueError("nota deve ser finita e estar no intervalo [0, 10]")
        notas.append(nota)

    if not notas:
        raise ValueError("deve haver ao menos uma nota valida")

    descartada = None
    if len(notas) == 4:
        idx_menor = notas.index(min(notas))
        descartada = float(notas.pop(idx_menor))

    soma = sum((Decimal(str(nota)) for nota in notas), Decimal(0))
    media_dec = (soma / len(notas)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    media = float(media_dec)

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
