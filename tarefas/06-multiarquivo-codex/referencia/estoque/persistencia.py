import json
from .modelos import Movimento


def carregar_movimentos(caminho) -> list[Movimento]:
    """Leia a lista JSON e valide os campos obrigatórios de cada movimento."""
    with open(caminho, encoding='utf-8') as arquivo:
        dados = json.load(arquivo)
    if not isinstance(dados, list):
        raise ValueError("esperada uma lista")
    movimentos = []
    for item in dados:
        if not isinstance(item, dict):
            raise ValueError("movimento deve ser objeto")
        sku, delta = item.get('sku'), item.get('delta')
        if not isinstance(sku, str) or not sku.strip() or type(delta) is not int:
            raise ValueError("SKU ou delta inválido")
        movimentos.append(Movimento(sku, delta))
    return movimentos
