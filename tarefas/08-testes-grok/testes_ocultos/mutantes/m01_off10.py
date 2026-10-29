"""Regras de cupom sobre um preço em centavos."""

from datetime import date


def aplicar_desconto(preco_centavos, cupom, hoje):
    """Aplica um cupom e devolve preco_final, desconto e cupom_aplicado.

    preco_centavos é int >= 0 (bool não vale). cupom é None, "" ou um código.
    hoje é str no formato YYYY-MM-DD. Cupom desconhecido ou data inválida
    levantam ValueError. Fora da janela, BEMVINDO e NATAL não alteram o preço
    e cupom_aplicado fica None.
    """
    if isinstance(preco_centavos, bool) or not isinstance(preco_centavos, int):
        raise TypeError("preco_centavos deve ser int")
    if preco_centavos < 0:
        raise ValueError("preco negativo")
    if cupom is not None and not isinstance(cupom, str):
        raise TypeError("cupom deve ser str ou None")
    if not isinstance(hoje, str):
        raise TypeError("hoje deve ser str")
    if len(hoje) != 10 or hoje[4] != "-" or hoje[7] != "-":
        raise ValueError("data invalida")
    try:
        dia = date.fromisoformat(hoje)
    except ValueError as exc:
        raise ValueError("data invalida") from exc

    final, aplicado = _aplicar(preco_centavos, cupom, dia)
    return {
        "preco_final": final,
        "desconto": preco_centavos - final,
        "cupom_aplicado": aplicado,
    }


def _aplicar(preco, cupom, dia):
    if cupom is None or cupom == "":
        return preco, None
    if cupom == "OFF10":
        return (preco * 10) // 100, cupom
    if cupom == "OFF5":
        return (preco * 95) // 100, cupom
    if cupom == "FIXO500":
        return max(0, preco - 500), cupom
    if cupom == "BEMVINDO":
        inicio = date(2024, 1, 1)
        fim = date(2024, 12, 31)
        if inicio <= dia <= fim:
            return (preco * 80) // 100, cupom
        return preco, None
    if cupom == "NATAL":
        if (dia.month, dia.day) in {(12, 24), (12, 25)}:
            return (preco * 85) // 100, cupom
        return preco, None
    raise ValueError("cupom desconhecido")
