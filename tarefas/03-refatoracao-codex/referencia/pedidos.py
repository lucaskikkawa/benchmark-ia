def subtotal(quantidade: int, preco_centavos: int, desconto_percentual: int = 0) -> int:
    """Subtotal em centavos, truncando o desconto uma vez por linha."""
    return quantidade * preco_centavos * (100 - desconto_percentual) // 100


def resumo_pedidos(pedidos) -> dict:
    """Some unidades e subtotais de cada categoria sem alterar os pedidos."""
    itens = 0
    total = 0
    por_categoria = {}
    for pedido in pedidos:
        valor = subtotal(pedido['quantidade'], pedido['preco_centavos'],
                         pedido.get('desconto_percentual', 0))
        itens += pedido['quantidade']
        total += valor
        categoria = pedido['categoria']
        por_categoria[categoria] = por_categoria.get(categoria, 0) + valor
    return {'itens': itens, 'total_centavos': total, 'por_categoria': por_categoria}
