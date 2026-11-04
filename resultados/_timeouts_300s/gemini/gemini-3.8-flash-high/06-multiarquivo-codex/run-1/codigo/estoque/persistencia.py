import json
from .modelos import Movimento

__all__ = ['carregar_movimentos']


def carregar_movimentos(caminho) -> list[Movimento]:
    with open(caminho, mode='r', encoding='utf-8') as f:
        dados = json.load(f)

    if not isinstance(dados, list):
        raise ValueError("O conteúdo JSON raiz deve ser uma lista.")

    movimentos: list[Movimento] = []
    for item in dados:
        if not isinstance(item, dict):
            raise ValueError("Cada elemento da lista deve ser um objeto JSON.")

        if 'sku' not in item or 'delta' not in item:
            raise ValueError("O objeto deve conter os campos 'sku' e 'delta'.")

        sku = item['sku']
        if not isinstance(sku, str) or not sku.strip():
            raise ValueError(
                "O campo 'sku' deve ser uma string com ao menos um caractere não branco."
            )

        delta = item['delta']
        if isinstance(delta, bool) or not isinstance(delta, int):
            raise ValueError(
                "O campo 'delta' deve ser um número inteiro (não booleano)."
            )

        movimentos.append(Movimento(sku=sku, delta=delta))

    return movimentos
