def subtotal(quantidade: int, preco_centavos: int, desconto_percentual: int = 0) -> int:
    return quantidade * preco_centavos * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos):
    total_itens = 0
    total_centavos = 0
    por_categoria = {}
    for pedido in pedidos:
        quantidade = pedido["quantidade"]
        valor = subtotal(
            quantidade,
            pedido["preco_centavos"],
            pedido.get("desconto_percentual", 0),
        )
        total_itens += quantidade
        total_centavos += valor
        categoria = pedido["categoria"]
        if categoria in por_categoria:
            por_categoria[categoria] += valor
        else:
            por_categoria[categoria] = valor
    return {
        "itens": total_itens,
        "total_centavos": total_centavos,
        "por_categoria": por_categoria,
    }
