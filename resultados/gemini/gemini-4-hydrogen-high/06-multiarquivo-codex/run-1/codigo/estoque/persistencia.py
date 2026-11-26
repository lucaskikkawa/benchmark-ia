import json
from os import PathLike

from .modelos import Movimento


def carregar_movimentos(caminho: str | PathLike[str]) -> list[Movimento]:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("O arquivo JSON deve conter uma lista de objetos.")

    movimentos: list[Movimento] = []
    for indice, item in enumerate(dados):
        if not isinstance(item, dict):
            raise ValueError(f"Item no índice {indice} deve ser um objeto JSON.")

        if "sku" not in item or "delta" not in item:
            raise ValueError(
                f"Item no índice {indice} deve conter os campos 'sku' e 'delta'."
            )

        sku = item["sku"]
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError(f"SKU inválido no índice {indice}.")

        delta = item["delta"]
        if isinstance(delta, bool) or not isinstance(delta, int):
            raise ValueError(f"Delta inválido no índice {indice}.")

        movimentos.append(Movimento(sku=sku, delta=delta))

    return movimentos
