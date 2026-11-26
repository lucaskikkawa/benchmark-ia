from collections.abc import Iterable, Mapping

from .modelos import Movimento


def calcular_saldos(
    movimentos: Iterable[Movimento],
    iniciais: Mapping[str, int] | None = None,
) -> dict[str, int]:
    saldos: dict[str, int] = dict(iniciais) if iniciais is not None else {}

    for sku, saldo in saldos.items():
        if saldo < 0:
            raise ValueError(f"Saldo inicial negativo para SKU {sku!r}: {saldo}")

    for movimento in movimentos:
        sku = movimento.sku
        novo_saldo = saldos.get(sku, 0) + movimento.delta
        if novo_saldo < 0:
            raise ValueError(f"Saldo negativo para SKU {sku!r}: {novo_saldo}")
        saldos[sku] = novo_saldo

    return saldos
