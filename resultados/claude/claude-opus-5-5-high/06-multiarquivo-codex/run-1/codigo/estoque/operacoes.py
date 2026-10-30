def calcular_saldos(movimentos, iniciais=None) -> dict[str, int]:
    saldos = {} if iniciais is None else dict(iniciais)
    for sku, saldo in saldos.items():
        if saldo < 0:
            raise ValueError(f"saldo inicial negativo para {sku!r}")
    for movimento in movimentos:
        sku = movimento.sku
        saldo = saldos.get(sku, 0) + movimento.delta
        if saldo < 0:
            raise ValueError(f"saldo negativo para {sku!r}")
        saldos[sku] = saldo
    return saldos

