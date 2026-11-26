from collections.abc import Iterable, Mapping
from typing import Any


def subtotal(
    quantidade: int,
    preco_centavos: int,
    desconto_percentual: int = 0,
) -> int:
    return quantidade * preco_centavos * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    total_itens = 0
    total_centavos = 0
    por_categoria: dict[str, int] = {}

    for pedido in pedidos:
        quantidade = pedido['quantidade']
        preco_centavos = pedido['preco_centavos']
        desconto_percentual = pedido.get('desconto_percentual', 0)
        categoria = pedido['categoria']

        subtotal_pedido = subtotal(
            quantidade,
            preco_centavos,
            desconto_percentual,
        )

        total_itens += quantidade
        total_centavos += subtotal_pedido
        por_categoria[categoria] = (
            por_categoria.get(categoria, 0) + subtotal_pedido
        )

    return {
        'itens': total_itens,
        'total_centavos': total_centavos,
        'por_categoria': por_categoria,
    }
