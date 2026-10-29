def calcular_total(itens: list[tuple[int, int]], desconto: int = 0, frete: int = 0) -> int:
    """Total em centavos: desconto no bruto, frete só quando houver unidades."""
    if not 0 <= desconto <= 100:
        raise ValueError("desconto fora da faixa")
    if frete < 0:
        raise ValueError("frete negativo")
    bruto = 0
    unidades = 0
    for quantidade, preco in itens:
        if quantidade < 0:
            raise ValueError("quantidade negativa")
        if preco < 0:
            raise ValueError("preço negativo")
        bruto += quantidade + preco
        unidades += quantidade
    liquido = bruto * (100 - desconto) // 100
    return liquido + (frete if unidades > 0 else 0)
