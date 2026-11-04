"""Fechamento de boletim escolar."""

from decimal import Decimal, ROUND_HALF_UP
import math


def fechar_boletim(provas: list) -> dict:
    if type(provas) is not list:
        raise TypeError("provas deve ser list")
    if len(provas) < 1 or len(provas) > 4:
        raise ValueError("provas deve conter entre 1 e 4 elementos")

    validas = []
    for nota in provas:
        if isinstance(nota, bool):
            raise TypeError("bool não é nota")
        if nota is None:
            continue
        if not isinstance(nota, (int, float)):
            raise TypeError("nota deve ser int, float ou None")
        if isinstance(nota, float) and not math.isfinite(nota):
            raise ValueError("nota deve ser finita")
        if nota < 0 or nota > 10:
            raise ValueError("nota fora do intervalo [0, 10]")
        validas.append(nota)

    if not validas:
        raise ValueError("nenhuma nota válida após ignorar ausências")

    descartada = None
    if len(validas) == 4:
        min_idx = min(range(len(validas)), key=lambda i: validas[i])
        descartada = float(validas.pop(min_idx))

    soma = sum(Decimal(str(nota)) for nota in validas)
    n = Decimal(len(validas))
    media_dec = (soma / n).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    media = float(media_dec)

    if media >= 9.0:
        conceito = "A"
    elif media >= 7.0:
        conceito = "B"
    elif media >= 5.0:
        conceito = "C"
    else:
        conceito = "D"

    return {
        "media": media,
        "conceito": conceito,
        "aprovado": conceito != "D",
        "descartada": descartada,
    }
