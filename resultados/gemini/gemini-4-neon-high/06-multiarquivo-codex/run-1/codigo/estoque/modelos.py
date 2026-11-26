from dataclasses import dataclass


@dataclass(frozen=True)
class Movimento:
    sku: str
    delta: int
