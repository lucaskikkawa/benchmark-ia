import json
from pathlib import Path

from .modelos import Movimento


def carregar_movimentos(caminho):
    with open(Path(caminho), encoding="utf-8") as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, list):
        raise ValueError("o JSON deve conter uma lista de movimentos")
    movimentos = []
    for i, item in enumerate(dados):
        if not isinstance(item, dict):
            raise ValueError(f"movimento {i} deve ser um objeto")
        if "sku" not in item or "delta" not in item:
            raise ValueError(f"movimento {i} sem campo 'sku' ou 'delta'")
        sku = item["sku"]
        delta = item["delta"]
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError(f"movimento {i} com sku inválido: {sku!r}")
        if type(delta) is not int:
            raise ValueError(f"movimento {i} com delta inválido: {delta!r}")
        movimentos.append(Movimento(sku, delta))
    return movimentos
