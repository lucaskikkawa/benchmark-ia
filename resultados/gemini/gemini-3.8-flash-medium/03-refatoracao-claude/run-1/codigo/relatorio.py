LIMITE_FAIXA_ALTA = 1000
TAXAS_DESCONTO: dict[str, tuple[float, float]] = {
    'vip': (0.10, 0.15),
    'atacado': (0.05, 0.08),
}
TAXAS_PADRAO: tuple[float, float] = (0.0, 0.02)


def calcular_subtotal(itens: list[dict]) -> float:
    """Soma preco * qtd dos itens. ValueError se algum qtd < 0. Lista vazia -> 0."""
    total = 0.0
    for item in itens:
        if item['qtd'] < 0:
            raise ValueError('qtd negativa')
        total += item['preco'] * item['qtd']
    return total


def calcular_desconto(subtotal: float, tipo_cliente: str) -> float:
    """Retorna o VALOR do desconto (não o total líquido) para o subtotal e o tipo de cliente."""
    try:
        taxas = TAXAS_DESCONTO.get(tipo_cliente, TAXAS_PADRAO)
    except TypeError:
        taxas = TAXAS_PADRAO
    taxa = taxas[1] if subtotal > LIMITE_FAIXA_ALTA else taxas[0]
    return subtotal * taxa


def formatar_relatorio(totais_por_cliente: dict[str, float]) -> str:
    """Gera o texto do relatório a partir do total líquido por cliente."""
    linhas = []
    tot = 0
    for cliente in sorted(totais_por_cliente.keys()):
        linhas.append(cliente + ': ' + ('%.2f' % totais_por_cliente[cliente]))
        tot = tot + totais_por_cliente[cliente]
    linhas.append('TOTAL: ' + ('%.2f' % tot))
    return '\n'.join(linhas)


def gerar_relatorio(pedidos: list[dict]) -> str:
    totais_por_cliente: dict[str, float] = {}
    for pedido in pedidos:
        cliente = pedido['cliente']
        subtotal = calcular_subtotal(pedido['itens'])
        desconto = calcular_desconto(subtotal, pedido['tipo'])
        total_liquido = subtotal - desconto
        if cliente in totais_por_cliente:
            totais_por_cliente[cliente] = totais_por_cliente[cliente] + total_liquido
        else:
            totais_por_cliente[cliente] = total_liquido
    return formatar_relatorio(totais_por_cliente)
