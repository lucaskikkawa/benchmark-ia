from collections.abc import Iterable, Mapping
from .modelos import Movimento


def calcular_saldos(
    movimentos: Iterable[Movimento],
    iniciais: Mapping[str, int] | None = None,
) -> dict[str, int]:
    saldos = dict(iniciais) if iniciais is not None else {}

    for sku, saldo in saldos.items():
        if saldo < 0:
            raise ValueError(f"Saldo inicial negativo para o SKU {sku!r}: {saldo}")

    for mov in movimentos:
        saldo = saldos.get(mov.sku, 0) + mov.delta
        if saldo < 0:
            raise ValueError(
                f"Saldo intermediário negativo para o SKU {mov.sku!r}: {saldo}"
            )
        saldos[mov.sku] = saldo

    return saldos
