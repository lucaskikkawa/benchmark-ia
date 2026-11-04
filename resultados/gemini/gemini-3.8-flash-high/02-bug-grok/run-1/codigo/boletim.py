"""Fechamento de boletim escolar seguindo o contrato de cálculo e validação."""

import math
from decimal import Decimal, ROUND_HALF_UP


def fechar_boletim(provas: list) -> dict:
    if type(provas) is not list:
        raise TypeError("provas deve ser list")

    if len(provas) == 0 or len(provas) > 4:
        raise ValueError("provas deve ter de 1 a 4 elementos")

    for nota in provas:
        if isinstance(nota, bool) or (nota is not None and not isinstance(nota, (int, float))):
            raise TypeError("nota deve ser int, float ou None")
        if nota is not None:
            if not math.isfinite(nota) or nota < 0 or nota > 10:
                raise ValueError("nota deve ser finita e estar no intervalo [0, 10]")

    validas = [nota for nota in provas if nota is not None]
    if len(validas) == 0:
        raise ValueError("depois de ignorar None não sobra nenhuma nota")

    descartada = None
    if len(validas) == 4:
        menor = min(validas)
        idx = validas.index(menor)
        descartada_val = validas.pop(idx)
        descartada = float(descartada_val)
        if descartada == 0.0:
            descartada = 0.0

    soma = sum(Decimal(str(nota)) for nota in validas)
    media_dec = (soma / len(validas)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    media = float(media_dec)
    if media == 0.0:
        media = 0.0

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
