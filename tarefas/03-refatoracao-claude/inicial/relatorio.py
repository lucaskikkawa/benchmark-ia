def gerar_relatorio(pedidos):
    r = {}
    for p in pedidos:
        c = p['cliente']
        t = 0
        for i in p['itens']:
            if i['qtd'] < 0:
                raise ValueError('qtd negativa')
            t = t + i['preco'] * i['qtd']
        if p['tipo'] == 'vip':
            if t > 1000:
                t = t - t * 0.15
            else:
                t = t - t * 0.10
        elif p['tipo'] == 'atacado':
            if t > 1000:
                t = t - t * 0.08
            else:
                t = t - t * 0.05
        else:
            if t > 1000:
                t = t - t * 0.02
            else:
                t = t - t * 0
        if c in r:
            r[c] = r[c] + t
        else:
            r[c] = t
    s = ''
    tot = 0
    for c in sorted(r.keys()):
        s = s + c + ': ' + ('%.2f' % r[c]) + '\n'
        tot = tot + r[c]
    s = s + 'TOTAL: ' + ('%.2f' % tot)
    return s
