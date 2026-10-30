def calcular_saldos(movimentos, iniciais=None):
    saldos = dict(iniciais) if iniciais is not None else {}

    for sku, saldo in saldos.items():
        if saldo < 0:
            raise ValueError(f"saldo inicial negativo para {sku!r}: {saldo}")

    for movimento in movimentos:
        atual = saldos.get(movimento.sku, 0) + movimento.delta
        if atual < 0:
            raise ValueError(f"saldo negativo para {movimento.sku!r}: {atual}")
        saldos[movimento.sku] = atual

    return saldos
