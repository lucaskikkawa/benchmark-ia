import json

from .modelos import Movimento


def carregar_movimentos(caminho) -> list[Movimento]:
    with open(caminho, encoding="utf-8") as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError("forma inválida: o JSON deve ser uma lista de movimentos")

    return [_interpretar_movimento(item, indice) for indice, item in enumerate(dados)]


def _interpretar_movimento(item, indice):
    if not isinstance(item, dict):
        raise ValueError(f"forma inválida: movimento {indice} não é um objeto")
    if "sku" not in item:
        raise ValueError(f"campo ausente: sku no movimento {indice}")
    if "delta" not in item:
        raise ValueError(f"campo ausente: delta no movimento {indice}")

    sku = item["sku"]
    delta = item["delta"]
    if not isinstance(sku, str) or not any(not caractere.isspace() for caractere in sku):
        raise ValueError(f"sku inválido no movimento {indice}")
    if isinstance(delta, bool) or not isinstance(delta, int):
        raise ValueError(f"delta inválido no movimento {indice}")
    return Movimento(sku, delta)
