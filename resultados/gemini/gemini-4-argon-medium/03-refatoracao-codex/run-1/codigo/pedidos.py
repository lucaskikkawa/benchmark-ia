from typing import Any, Iterable


def subtotal(quantidade: int, preco_centavos: int, desconto_percentual: int = 0) -> int:
    return quantidade * preco_centavos * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos: Iterable[dict[str, Any]]) -> dict[str, Any]:
    total_itens = 0
    total_centavos = 0
    totais_por_categoria: dict[str, int] = {}

    for pedido in pedidos:
        quantidade = pedido['quantidade']
        preco_centavos = pedido['preco_centavos']
        desconto_percentual = pedido.get('desconto_percentual', 0)
        categoria = pedido['categoria']

        valor_subtotal = subtotal(quantidade, preco_centavos, desconto_percentual)

        total_itens += quantidade
        total_centavos += valor_subtotal
        totais_por_categoria[categoria] = totais_por_categoria.get(categoria, 0) + valor_subtotal

    return {
        'itens': total_itens,
        'total_centavos': total_centavos,
        'por_categoria': totais_por_categoria,
    }
