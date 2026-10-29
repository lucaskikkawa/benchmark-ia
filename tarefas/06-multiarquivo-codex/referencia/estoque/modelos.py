from dataclasses import dataclass


@dataclass(frozen=True)
class Movimento:
    """Alteração inteira do saldo de um SKU."""
    sku: str
    delta: int
