import json

from .modelos import Movimento


def carregar_movimentos(caminho) -> list[Movimento]:
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("forma inválida")

    movimentos = []
    for item in dados:
        if not isinstance(item, dict):
            raise ValueError("forma inválida")
        if "sku" not in item or "delta" not in item:
            raise ValueError("campos ausentes")
        sku = item["sku"]
        delta = item["delta"]
        if not isinstance(sku, str) or sku.strip() == "":
            raise ValueError("sku inválido")
        if isinstance(delta, bool) or not isinstance(delta, int):
            raise ValueError("delta inválido")
        movimentos.append(Movimento(sku=sku, delta=delta))
    return movimentos
