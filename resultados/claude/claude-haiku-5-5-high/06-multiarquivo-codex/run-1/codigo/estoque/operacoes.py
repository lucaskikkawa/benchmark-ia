def calcular_saldos(movimentos, iniciais=None) -> dict[str, int]:
    """Aplica os movimentos na ordem e devolve um dict novo de saldos.

    Lança ValueError se algum saldo inicial ou intermediário ficar negativo.
    """
    saldos = dict(iniciais) if iniciais is not None else {}
    for sku, saldo in saldos.items():
        if saldo < 0:
            raise ValueError(f"saldo inicial negativo para {sku!r}: {saldo}")

    for movimento in movimentos:
        saldo = saldos.get(movimento.sku, 0) + movimento.delta
        if saldo < 0:
            raise ValueError(f"saldo negativo para {movimento.sku!r}: {saldo}")
        saldos[movimento.sku] = saldo

    return saldos
