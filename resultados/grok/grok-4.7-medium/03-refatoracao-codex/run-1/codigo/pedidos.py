def subtotal(quantidade: int, preco_centavos: int, desconto_percentual: int = 0) -> int:
    return quantidade * preco_centavos * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos):
    itens = 0
    total_centavos = 0
    por_categoria = {}
    for pedido in pedidos:
        itens += pedido['quantidade']
        valor = subtotal(
            pedido['quantidade'],
            pedido['preco_centavos'],
            pedido.get('desconto_percentual', 0),
        )
        total_centavos += valor
        categoria = pedido['categoria']
        por_categoria[categoria] = por_categoria.get(categoria, 0) + valor
    return {
        'itens': itens,
        'total_centavos': total_centavos,
        'por_categoria': por_categoria,
    }
