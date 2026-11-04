def subtotal(quantidade: int, preco_centavos: int, desconto_percentual: int = 0) -> int:
    return quantidade * preco_centavos * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos):
    total_itens = 0
    total_centavos = 0
    por_categoria = {}

    for pedido in pedidos:
        quantidade = pedido['quantidade']
        preco_centavos = pedido['preco_centavos']
        categoria = pedido['categoria']
        desconto_percentual = pedido.get('desconto_percentual', 0)

        subtotal_item = subtotal(quantidade, preco_centavos, desconto_percentual)

        total_itens += quantidade
        total_centavos += subtotal_item

        if categoria in por_categoria:
            por_categoria[categoria] += subtotal_item
        else:
            por_categoria[categoria] = subtotal_item

    return {
        'itens': total_itens,
        'total_centavos': total_centavos,
        'por_categoria': por_categoria,
    }
