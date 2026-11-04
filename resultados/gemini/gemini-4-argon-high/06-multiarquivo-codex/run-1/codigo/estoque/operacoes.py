from collections.abc import Iterable
from .modelos import Movimento


def calcular_saldos(
    movimentos: Iterable[Movimento],
    iniciais: dict[str, int] | None = None,
) -> dict[str, int]:
    saldos: dict[str, int] = {} if iniciais is None else dict(iniciais)
    for sku, saldo in saldos.items():
        if saldo < 0:
            raise ValueError(f"Saldo inicial negativo para SKU {sku!r}: {saldo}")

    for movimento in movimentos:
        novo_saldo = saldos.get(movimento.sku, 0) + movimento.delta
        if novo_saldo < 0:
            raise ValueError(
                f"Saldo intermediário negativo para SKU {movimento.sku!r}: {novo_saldo}"
            )
        saldos[movimento.sku] = novo_saldo

    return saldos
