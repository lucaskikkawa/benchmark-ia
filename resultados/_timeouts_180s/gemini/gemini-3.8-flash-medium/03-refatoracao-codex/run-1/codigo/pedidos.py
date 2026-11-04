def resumo_pedidos(pedidos):
    a = 0
    b = 0
    c = {}
    for x in pedidos:
        a = a + x['quantidade']
        y = x['quantidade'] * x['preco_centavos'] * (100 - x.get('desconto_percentual', 0)) // 100
        b = b + y
        if x['categoria'] in c:
            c[x['categoria']] = c[x['categoria']] + y
        else:
            c[x['categoria']] = y
    return {'itens': a, 'total_centavos': b, 'por_categoria': c}
