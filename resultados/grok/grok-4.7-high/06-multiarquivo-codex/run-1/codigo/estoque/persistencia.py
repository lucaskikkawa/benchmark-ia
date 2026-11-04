import json

from .modelos import Movimento


def carregar_movimentos(caminho) -> list[Movimento]:
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("o arquivo deve conter uma lista de movimentos")

    movimentos = []
    for item in dados:
        if not isinstance(item, dict):
            raise ValueError("cada movimento deve ser um objeto")
        try:
            sku = item["sku"]
        except KeyError:
            raise ValueError("campo sku ausente") from None
        try:
            delta = item["delta"]
        except KeyError:
            raise ValueError("campo delta ausente") from None

        if not isinstance(sku, str) or all(caractere.isspace() for caractere in sku):
            raise ValueError("sku inválido")
        if isinstance(delta, bool) or not isinstance(delta, int):
            raise ValueError("delta inválido")

        movimentos.append(Movimento(sku, delta))

    return movimentos
