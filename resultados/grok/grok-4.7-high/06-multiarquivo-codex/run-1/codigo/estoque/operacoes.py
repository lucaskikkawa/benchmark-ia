def calcular_saldos(movimentos, iniciais=None) -> dict[str, int]:
    if iniciais is None:
        saldos = {}
    else:
        saldos = dict(iniciais)
        for sku, saldo in saldos.items():
            if saldo < 0:
                raise ValueError(f"saldo inicial negativo para {sku!r}: {saldo}")

    for movimento in movimentos:
        sku = movimento.sku
        novo = saldos.get(sku, 0) + movimento.delta
        if novo < 0:
            raise ValueError(f"saldo negativo para {sku!r}: {novo}")
        saldos[sku] = novo

    return saldos
