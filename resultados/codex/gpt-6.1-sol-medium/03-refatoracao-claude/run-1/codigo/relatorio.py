LIMITE_FAIXA_ALTA = 1000
TAXAS_DESCONTO: dict[str, tuple[float, float]] = {
    'vip': (0.10, 0.15),
    'atacado': (0.05, 0.08),
}
TAXAS_PADRAO: tuple[float, float] = (0, 0.02)


def calcular_subtotal(itens: list[dict]) -> float:
    """Soma preco * qtd dos itens; rejeita quantidades negativas."""
    subtotal = 0
    for item in itens:
        if item['qtd'] < 0:
            raise ValueError('qtd negativa')
        subtotal = subtotal + item['preco'] * item['qtd']
    return subtotal


def calcular_desconto(subtotal: float, tipo_cliente: str) -> float:
    """Retorna o valor do desconto usando as taxas e o limite atuais."""
    taxas = TAXAS_PADRAO
    # Comparar por igualdade preserva também tipos desconhecidos não hashable.
    for tipo, taxas_do_tipo in TAXAS_DESCONTO.items():
        if tipo_cliente == tipo:
            taxas = taxas_do_tipo
            break
    taxa = taxas[1] if subtotal > LIMITE_FAIXA_ALTA else taxas[0]
    return subtotal * taxa


def formatar_relatorio(totais_por_cliente: dict[str, float]) -> str:
    """Formata os clientes em ordem e soma seus totais nessa mesma ordem."""
    texto = ''
    total = 0
    for cliente in sorted(totais_por_cliente.keys()):
        texto = texto + cliente + ': ' + ('%.2f' % totais_por_cliente[cliente]) + '\n'
        total = total + totais_por_cliente[cliente]
    return texto + 'TOTAL: ' + ('%.2f' % total)


def gerar_relatorio(pedidos: list[dict]) -> str:
    """Calcula os valores líquidos por cliente e gera o relatório."""
    totais_por_cliente = {}
    for pedido in pedidos:
        cliente = pedido['cliente']
        subtotal = calcular_subtotal(pedido['itens'])
        total_liquido = subtotal - calcular_desconto(subtotal, pedido['tipo'])
        if cliente in totais_por_cliente:
            totais_por_cliente[cliente] = totais_por_cliente[cliente] + total_liquido
        else:
            totais_por_cliente[cliente] = total_liquido
    return formatar_relatorio(totais_por_cliente)
