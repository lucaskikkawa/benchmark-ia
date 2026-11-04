def subtotal(quantidade: int, preco_centavos: int, desconto_percentual: int = 0) -> int:
    """Subtotal de uma linha em centavos, com truncamento aplicado à linha inteira."""
    return quantidade * preco_centavos * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos):
    total_itens = 0
    total_centavos = 0
    por_categoria = {}
    for pedido in pedidos:
        quantidade = pedido['quantidade']
        total_itens = total_itens + quantidade
        valor_linha = subtotal(
            quantidade,
            pedido['preco_centavos'],
            pedido.get('desconto_percentual', 0),
        )
        total_centavos = total_centavos + valor_linha
        categoria = pedido['categoria']
        if categoria in por_categoria:
            por_categoria[categoria] = por_categoria[categoria] + valor_linha
        else:
            por_categoria[categoria] = valor_linha
    return {'itens': total_itens, 'total_centavos': total_centavos, 'por_categoria': por_categoria}
