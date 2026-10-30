def calcular_saldos(movimentos, iniciais=None) -> dict[str, int]:
    if iniciais is None:
        saldos = {}
    else:
        saldos = dict(iniciais)
        for valor in saldos.values():
            if valor < 0:
                raise ValueError("saldo inicial negativo")

    for movimento in movimentos:
        sku = movimento.sku
        novo = saldos.get(sku, 0) + movimento.delta
        if novo < 0:
            raise ValueError("saldo negativo")
        saldos[sku] = novo
    return saldos
