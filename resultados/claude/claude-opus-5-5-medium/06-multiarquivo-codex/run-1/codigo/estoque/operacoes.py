def calcular_saldos(movimentos, iniciais=None):
    saldos = dict(iniciais) if iniciais is not None else {}
    for sku, saldo in saldos.items():
        if saldo < 0:
            raise ValueError(f"saldo inicial negativo para {sku!r}: {saldo}")
    for mov in movimentos:
        novo = saldos.get(mov.sku, 0) + mov.delta
        if novo < 0:
            raise ValueError(f"saldo negativo para {mov.sku!r}: {novo}")
        saldos[mov.sku] = novo
    return saldos
