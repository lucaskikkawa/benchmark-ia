LIMITE_FAIXA_ALTA = 1000
TAXAS_DESCONTO: dict[str, tuple[float, float]] = {
    'vip': (0.10, 0.15),
    'atacado': (0.05, 0.08),
}
# 0 (int), não 0.0: `subtotal * 0` preserva inteiros enormes, como no código original.
TAXAS_PADRAO: tuple[float, float] = (0, 0.02)


def calcular_subtotal(itens: list[dict]) -> float:
    """Soma preco * qtd dos itens. ValueError se algum qtd < 0. Lista vazia -> 0."""
    t = 0
    for i in itens:
        if i['qtd'] < 0:
            raise ValueError('qtd negativa')
        t = t + i['preco'] * i['qtd']
    return t


def calcular_desconto(subtotal: float, tipo_cliente: str) -> float:
    """Retorna o VALOR do desconto (não o total líquido) para o subtotal e o tipo de cliente."""
    taxa_baixa, taxa_alta = TAXAS_PADRAO
    for tipo, taxas in TAXAS_DESCONTO.items():
        if tipo_cliente == tipo:
            taxa_baixa, taxa_alta = taxas
            break
    if subtotal > LIMITE_FAIXA_ALTA:
        taxa = taxa_alta
    else:
        taxa = taxa_baixa
    return subtotal * taxa


def formatar_relatorio(totais_por_cliente: dict[str, float]) -> str:
    """Gera o texto do relatório a partir do total líquido por cliente."""
    s = ''
    tot = 0
    for c in sorted(totais_por_cliente.keys()):
        s = s + c + ': ' + ('%.2f' % totais_por_cliente[c]) + '\n'
        tot = tot + totais_por_cliente[c]
    s = s + 'TOTAL: ' + ('%.2f' % tot)
    return s


def gerar_relatorio(pedidos: list[dict]) -> str:
    r = {}
    for p in pedidos:
        c = p['cliente']
        sub = calcular_subtotal(p['itens'])
        t = sub - calcular_desconto(sub, p['tipo'])
        if c in r:
            r[c] = r[c] + t
        else:
            r[c] = t
    return formatar_relatorio(r)
