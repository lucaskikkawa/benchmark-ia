import json
from pathlib import Path
from typing import Union

from .modelos import Movimento


def carregar_movimentos(caminho: Union[str, Path]) -> list[Movimento]:
    with open(caminho, mode="r", encoding="utf-8") as f:
        dados = json.load(f)

    if not isinstance(dados, list):
        raise ValueError("O conteúdo JSON deve ser uma lista de objetos.")

    movimentos: list[Movimento] = []
    for item in dados:
        if not isinstance(item, dict):
            raise ValueError("Cada item da lista deve ser um objeto JSON.")
        if "sku" not in item:
            raise ValueError("Campo obrigatório 'sku' ausente.")
        if "delta" not in item:
            raise ValueError("Campo obrigatório 'delta' ausente.")

        sku = item["sku"]
        delta = item["delta"]

        if not isinstance(sku, str) or not sku.strip():
            raise ValueError("Campo 'sku' deve ser uma string com ao menos um caractere não branco.")
        if isinstance(delta, bool) or not isinstance(delta, int):
            raise ValueError("Campo 'delta' deve ser um inteiro (bool não é aceito).")

        movimentos.append(Movimento(sku=sku, delta=delta))

    return movimentos
