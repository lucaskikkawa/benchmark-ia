from typing import Any, Iterable, Mapping, Optional


def calcular_saldos(
    movimentos: Iterable[Any], iniciais: Optional[Mapping[str, int]] = None
) -> dict[str, int]:
    saldos: dict[str, int] = dict(iniciais) if iniciais is not None else {}
    for sku, saldo in saldos.items():
        if saldo < 0:
            raise ValueError(f"Saldo inicial negativo para SKU {sku!r}: {saldo}")

    for mov in movimentos:
        novo_saldo = saldos.get(mov.sku, 0) + mov.delta
        if novo_saldo < 0:
            raise ValueError(f"Saldo negativo para SKU {mov.sku!r}: {novo_saldo}")
        saldos[mov.sku] = novo_saldo

    return saldos
