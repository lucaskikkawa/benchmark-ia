import json
from os import PathLike

from .modelos import Movimento


def carregar_movimentos(caminho: str | PathLike[str]) -> list[Movimento]:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("O conteúdo JSON deve ser uma lista de objetos.")

    movimentos: list[Movimento] = []
    for item in dados:
        if not isinstance(item, dict):
            raise ValueError("Cada item da lista deve ser um objeto JSON.")
        if "sku" not in item or "delta" not in item:
            raise ValueError("Os campos 'sku' e 'delta' são obrigatórios.")

        sku = item["sku"]
        delta = item["delta"]

        if not isinstance(sku, str) or not sku.strip():
            raise ValueError("O campo 'sku' deve ser uma string não vazia.")
        if isinstance(delta, bool) or not isinstance(delta, int):
            raise ValueError("O campo 'delta' deve ser um inteiro.")

        movimentos.append(Movimento(sku=sku, delta=delta))

    return movimentos

