from collections.abc import Iterable, Mapping

from .modelos import Movimento


def calcular_saldos(
    movimentos: Iterable[Movimento],
    iniciais: Mapping[str, int] | None = None,
) -> dict[str, int]:
    saldos: dict[str, int] = {}
    if iniciais is not None:
        for sku, saldo in iniciais.items():
            if saldo < 0:
                raise ValueError(f"Saldo inicial negativo para SKU {sku!r}: {saldo}")
            saldos[sku] = saldo

    for movimento in movimentos:
        novo_saldo = saldos.get(movimento.sku, 0) + movimento.delta
        if novo_saldo < 0:
            raise ValueError(
                f"Saldo negativo para SKU {movimento.sku!r}: {novo_saldo}"
            )
        saldos[movimento.sku] = novo_saldo

    return saldos
