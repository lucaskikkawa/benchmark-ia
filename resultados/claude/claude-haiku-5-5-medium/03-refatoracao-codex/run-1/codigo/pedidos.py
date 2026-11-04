def subtotal(quantidade: int, preco_centavos: int, desconto_percentual: int = 0) -> int:
    # Truncamento feito por linha, após aplicar o desconto sobre o valor bruto.
    valor_bruto = quantidade * preco_centavos
    return valor_bruto * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos):
    total_itens = 0
    total_centavos = 0
    subtotais_por_categoria = {}
    for pedido in pedidos:
        total_itens = total_itens + pedido['quantidade']
        subtotal_pedido = subtotal(
            pedido['quantidade'],
            pedido['preco_centavos'],
            pedido.get('desconto_percentual', 0),
        )
        total_centavos = total_centavos + subtotal_pedido
        categoria = pedido['categoria']
        if categoria in subtotais_por_categoria:
            subtotais_por_categoria[categoria] = subtotais_por_categoria[categoria] + subtotal_pedido
        else:
            subtotais_por_categoria[categoria] = subtotal_pedido
    return {
        'itens': total_itens,
        'total_centavos': total_centavos,
        'por_categoria': subtotais_por_categoria,
    }
