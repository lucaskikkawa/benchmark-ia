"""Fechamento de boletim com descarte condicional e média half-up."""

import math
from decimal import Decimal, ROUND_HALF_UP

_MAX_PROVAS = 4
_FAIXAS = (
    (Decimal("9.00"), "A"),
    (Decimal("7.00"), "B"),
    (Decimal("5.00"), "C"),
)


def fechar_boletim(provas: list) -> dict:
    """Resume até 4 provas.

    None é ausência e não entra na média. A menor nota só é descartada quando
    existem exatamente 4 notas válidas. A média usa Decimal(str(nota)) e
    ROUND_HALF_UP em duas casas. Conceitos: >= 9 A, >= 7 B, >= 5 C, senão D.
    Levanta TypeError para tipos inválidos e ValueError para quantidade ou
    nota fora de [0, 10]. Não altera a lista recebida.
    """
    if not isinstance(provas, list):
        raise TypeError("provas deve ser list")
    if len(provas) == 0 or len(provas) > _MAX_PROVAS:
        raise ValueError("quantidade de provas invalida")

    validas: list[int | float] = []
    for nota in provas:
        if nota is None:
            continue
        if isinstance(nota, bool) or not isinstance(nota, (int, float)):
            raise TypeError("nota invalida")
        if isinstance(nota, float) and not math.isfinite(nota):
            raise ValueError("nota invalida")
        if nota < 0 or nota > 10:
            raise ValueError("nota invalida")
        validas.append(nota)
    if not validas:
        raise ValueError("sem notas validas")

    descartada = None
    if len(validas) == _MAX_PROVAS:
        menor = min(validas)
        validas.remove(menor)
        descartada = float(menor)

    total = sum((Decimal(str(nota)) for nota in validas), Decimal("0"))
    media_dec = (total / Decimal(len(validas))).quantize(
        Decimal("0.01"),
        rounding=ROUND_HALF_UP,
    )
    conceito = _conceito(media_dec)
    return {
        "media": float(media_dec),
        "conceito": conceito,
        "aprovado": conceito != "D",
        "descartada": descartada,
    }


def _conceito(media: Decimal) -> str:
    for limite, nome in _FAIXAS:
        if media >= limite:
            return nome
    return "D"
