def calcular_saldos(movimentos, iniciais=None) -> dict[str, int]:
    saldos = {} if iniciais is None else dict(iniciais)
    for saldo in saldos.values():
        if saldo < 0:
            raise ValueError("saldo inicial negativo")

    for movimento in movimentos:
        sku = movimento.sku
        novo = saldos.get(sku, 0) + movimento.delta
        if novo < 0:
            raise ValueError("saldo negativo")
        saldos[sku] = novo
    return saldos
