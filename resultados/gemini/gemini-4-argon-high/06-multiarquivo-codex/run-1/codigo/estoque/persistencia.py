import json
from pathlib import Path
from .modelos import Movimento


def carregar_movimentos(caminho: str | Path) -> list[Movimento]:
    with Path(caminho).open("r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("O arquivo JSON deve conter uma lista de movimentos.")

    movimentos: list[Movimento] = []
    for item in dados:
        if not isinstance(item, dict):
            raise ValueError("Cada movimento deve ser um objeto JSON.")
        if "sku" not in item or "delta" not in item:
            raise ValueError("Campos 'sku' e 'delta' são obrigatórios.")

        sku = item["sku"]
        delta = item["delta"]

        if not isinstance(sku, str) or not sku.strip():
            raise ValueError("Campo 'sku' deve ser uma string não vazia.")
        if not isinstance(delta, int) or isinstance(delta, bool):
            raise ValueError("Campo 'delta' deve ser um inteiro.")

        movimentos.append(Movimento(sku=sku, delta=delta))

    return movimentos
