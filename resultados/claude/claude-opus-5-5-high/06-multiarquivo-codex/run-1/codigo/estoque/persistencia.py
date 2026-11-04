import json
from decimal import Decimal

from .modelos import Movimento


def _parse_int(texto):
    # Evita o limite de dígitos de int(str) preservando precisão arbitrária.
    return int(Decimal(texto))


def carregar_movimentos(caminho) -> list[Movimento]:
    with open(caminho, encoding='utf-8') as arquivo:
        texto = arquivo.read()
    try:
        dados = json.loads(texto, parse_int=_parse_int)
    except RecursionError as erro:
        raise ValueError("JSON aninhado demais") from erro

    if not isinstance(dados, list):
        raise ValueError("o JSON deve conter uma lista de movimentos")

    movimentos = []
    for indice, item in enumerate(dados):
        if not isinstance(item, dict):
            raise ValueError(f"movimento {indice} não é um objeto")
        if 'sku' not in item or 'delta' not in item:
            raise ValueError(f"movimento {indice} sem 'sku' ou 'delta'")
        sku = item['sku']
        delta = item['delta']
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError(f"movimento {indice} com sku inválido: {sku!r}")
        if type(delta) is not int:
            raise ValueError(f"movimento {indice} com delta inválido: {delta!r}")
        movimentos.append(Movimento(sku, delta))
    return movimentos
