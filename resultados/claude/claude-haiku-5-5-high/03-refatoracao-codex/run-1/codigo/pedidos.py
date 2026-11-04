def subtotal(quantidade: int, preco_centavos: int, desconto_percentual: int = 0) -> int:
    return quantidade * preco_centavos * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos):
    total_itens = 0
    total_centavos = 0
    subtotais_por_categoria = {}
    for pedido in pedidos:
        total_itens += pedido['quantidade']
        valor_linha = subtotal(
            pedido['quantidade'],
            pedido['preco_centavos'],
            pedido.get('desconto_percentual', 0),
        )
        total_centavos += valor_linha
        categoria = pedido['categoria']
        subtotais_por_categoria[categoria] = subtotais_por_categoria.get(categoria, 0) + valor_linha
    return {
        'itens': total_itens,
        'total_centavos': total_centavos,
        'por_categoria': subtotais_por_categoria,
    }
