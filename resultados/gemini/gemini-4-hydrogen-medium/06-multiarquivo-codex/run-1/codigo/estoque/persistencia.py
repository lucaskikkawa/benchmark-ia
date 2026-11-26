import json
import os

from .modelos import Movimento


def carregar_movimentos(caminho: str | os.PathLike[str]) -> list[Movimento]:
    with open(caminho, "r", encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("O arquivo JSON deve conter uma lista de movimentos.")

    movimentos: list[Movimento] = []
    for item in dados:
        if not isinstance(item, dict):
            raise ValueError("Cada movimento deve ser um objeto JSON.")
        if "sku" not in item or "delta" not in item:
            raise ValueError("Cada movimento deve conter os campos 'sku' e 'delta'.")

        sku = item["sku"]
        delta = item["delta"]

        if not isinstance(sku, str) or not sku.strip():
            raise ValueError("Campo 'sku' deve ser uma string nao vazia.")
        if isinstance(delta, bool) or not isinstance(delta, int):
            raise ValueError("Campo 'delta' deve ser um inteiro (nao bool).")

        movimentos.append(Movimento(sku=sku, delta=delta))

    return movimentos
