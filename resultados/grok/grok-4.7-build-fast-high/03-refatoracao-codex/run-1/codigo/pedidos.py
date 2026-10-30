def subtotal(quantidade: int, preco_centavos: int, desconto_percentual: int = 0) -> int:
    return quantidade * preco_centavos * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos):
    itens = 0
    total_centavos = 0
    por_categoria = {}
    for pedido in pedidos:
        quantidade = pedido['quantidade']
        valor_linha = subtotal(
            quantidade,
            pedido['preco_centavos'],
            pedido.get('desconto_percentual', 0),
        )
        itens += quantidade
        total_centavos += valor_linha
        categoria = pedido['categoria']
        if categoria in por_categoria:
            por_categoria[categoria] += valor_linha
        else:
            por_categoria[categoria] = valor_linha
    return {
        'itens': itens,
        'total_centavos': total_centavos,
        'por_categoria': por_categoria,
    }
