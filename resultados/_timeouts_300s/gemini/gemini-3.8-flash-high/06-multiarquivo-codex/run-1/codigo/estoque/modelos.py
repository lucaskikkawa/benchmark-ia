from dataclasses import dataclass

__all__ = ['Movimento']


@dataclass(frozen=True)
class Movimento:
    sku: str
    delta: int
