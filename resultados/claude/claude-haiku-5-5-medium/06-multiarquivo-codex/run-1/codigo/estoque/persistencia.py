import json

from .modelos import Movimento


def carregar_movimentos(caminho):
    with open(caminho, encoding='utf-8') as arquivo:
        dados = json.load(arquivo)

    if not isinstance(dados, list):
        raise ValueError('o JSON deve conter uma lista de objetos')

    movimentos = []
    for item in dados:
        if not isinstance(item, dict):
            raise ValueError('cada movimento deve ser um objeto')
        if 'sku' not in item or 'delta' not in item:
            raise ValueError('movimento sem campo "sku" ou "delta"')

        sku = item['sku']
        delta = item['delta']
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError(f'SKU inválido: {sku!r}')
        if not isinstance(delta, int) or isinstance(delta, bool):
            raise ValueError(f'delta inválido para {sku!r}: {delta!r}')

        movimentos.append(Movimento(sku=sku, delta=delta))

    return movimentos
