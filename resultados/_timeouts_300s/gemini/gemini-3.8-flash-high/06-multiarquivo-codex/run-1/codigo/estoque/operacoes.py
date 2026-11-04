from .modelos import Movimento

__all__ = ['calcular_saldos']


def calcular_saldos(movimentos, iniciais=None) -> dict[str, int]:
    saldos = dict(iniciais) if iniciais is not None else {}
    for sku, saldo in saldos.items():
        if saldo < 0:
            raise ValueError(
                f"Saldo inicial não pode ser negativo para o SKU '{sku}': {saldo}"
            )

    for m in movimentos:
        novo_saldo = saldos.get(m.sku, 0) + m.delta
        if novo_saldo < 0:
            raise ValueError(
                f"Saldo não pode ser negativo para o SKU '{m.sku}': {novo_saldo}"
            )
        saldos[m.sku] = novo_saldo

    return saldos
