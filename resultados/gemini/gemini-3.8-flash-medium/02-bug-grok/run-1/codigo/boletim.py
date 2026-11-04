"""Fechamento de boletim."""

from decimal import Decimal, ROUND_HALF_UP
import math


def fechar_boletim(provas: list) -> dict:
    if type(provas) is not list:
        raise TypeError("provas deve ser list")

    if len(provas) == 0 or len(provas) > 4:
        raise ValueError("provas deve ter entre 1 e 4 elementos")

    notas = []
    for nota in provas:
        if nota is None:
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota deve ser int ou float")
        if not math.isfinite(nota) or nota < 0 or nota > 10:
            raise ValueError("nota deve ser finita e estar no intervalo [0, 10]")
        notas.append(nota)

    if len(notas) == 0:
        raise ValueError("nenhuma nota valida apos ignorar ausencias")

    descartada = None
    if len(notas) == 4:
        menor_idx = min(range(4), key=lambda i: notas[i])
        descartada = float(notas.pop(menor_idx))
        if descartada == 0.0:
            descartada = 0.0

    soma = sum(Decimal(str(nota)) for nota in notas)
    n = Decimal(len(notas))
    media_dec = (soma / n).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    media = float(media_dec)
    if media == 0.0:
        media = 0.0

    if media >= 9.0:
        conceito = "A"
    elif media >= 7.0:
        conceito = "B"
    elif media >= 5.0:
        conceito = "C"
    else:
        conceito = "D"

    aprovado = conceito != "D"

    return {
        "media": media,
        "conceito": conceito,
        "aprovado": aprovado,
        "descartada": descartada,
    }
