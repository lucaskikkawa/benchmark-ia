from collections.abc import Iterable
from typing import Any


def subtotal(quantidade: int, preco_centavos: int, desconto_percentual: int = 0) -> int:
    return quantidade * preco_centavos * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos: Iterable[dict[str, Any]]) -> dict[str, Any]:
    total_itens = 0
    total_centavos = 0
    por_categoria: dict[str, int] = {}

    for pedido in pedidos:
        categoria = pedido['categoria']
        quantidade = pedido['quantidade']
        preco_centavos = pedido['preco_centavos']
        desconto_percentual = pedido.get('desconto_percentual', 0)

        total_itens += quantidade
        subtotal_pedido = subtotal(quantidade, preco_centavos, desconto_percentual)
        total_centavos += subtotal_pedido

        if categoria in por_categoria:
            por_categoria[categoria] += subtotal_pedido
        else:
            por_categoria[categoria] = subtotal_pedido

    return {
        'itens': total_itens,
        'total_centavos': total_centavos,
        'por_categoria': por_categoria,
    }

