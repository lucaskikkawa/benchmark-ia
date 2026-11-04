import json
from pathlib import Path

from .modelos import Movimento


def carregar_movimentos(caminho: str | Path) -> list[Movimento]:
    with open(caminho, "r", encoding="utf-8") as f:
        dados = json.load(f)

    if not isinstance(dados, list):
        raise ValueError("JSON raiz deve ser uma lista de objetos")

    movimentos: list[Movimento] = []
    for item in dados:
        if not isinstance(item, dict):
            raise ValueError(f"Elemento da lista não é um objeto JSON: {item!r}")
        if "sku" not in item:
            raise ValueError("Campo 'sku' ausente no objeto")
        if "delta" not in item:
            raise ValueError("Campo 'delta' ausente no objeto")

        sku = item["sku"]
        delta = item["delta"]

        if not isinstance(sku, str) or not sku.strip():
            raise ValueError(f"SKU inválido: {sku!r}")
        if isinstance(delta, bool) or not isinstance(delta, int):
            raise ValueError(f"Delta inválido: {delta!r}")

        movimentos.append(Movimento(sku=sku, delta=delta))

    return movimentos
