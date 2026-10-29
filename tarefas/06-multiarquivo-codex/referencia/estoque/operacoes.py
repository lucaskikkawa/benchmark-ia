def calcular_saldos(movimentos, iniciais=None) -> dict[str, int]:
    """Aplique movimentos na ordem, rejeitando qualquer saldo intermediário negativo."""
    saldos = dict(iniciais) if iniciais is not None else {}
    if any(saldo < 0 for saldo in saldos.values()):
        raise ValueError("saldo inicial negativo")
    for movimento in movimentos:
        saldo = saldos.get(movimento.sku, 0) + movimento.delta
        if saldo < 0:
            raise ValueError("saldo insuficiente")
        saldos[movimento.sku] = saldo
    return saldos
