import json

from .modelos import Movimento


def _validar_sku(sku):
    if not isinstance(sku, str) or not sku.strip():
        raise ValueError(f"SKU inválido: {sku!r}")
    return sku


def _validar_delta(delta):
    if isinstance(delta, bool) or not isinstance(delta, int):
        raise ValueError(f"delta inválido: {delta!r}")
    return delta


def carregar_movimentos(caminho) -> list[Movimento]:
    """Lê um JSON UTF-8 com uma lista de objetos {"sku": str, "delta": int}."""
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("o JSON deve conter uma lista de movimentos")

    movimentos = []
    for item in dados:
        if not isinstance(item, dict):
            raise ValueError(f"movimento deve ser um objeto: {item!r}")
        if "sku" not in item or "delta" not in item:
            raise ValueError(f"movimento sem campo obrigatório: {item!r}")
        movimentos.append(
            Movimento(_validar_sku(item["sku"]), _validar_delta(item["delta"]))
        )
    return movimentos
