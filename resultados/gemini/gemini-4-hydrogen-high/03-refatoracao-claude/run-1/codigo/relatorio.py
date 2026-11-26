LIMITE_FAIXA_ALTA = 1000
TAXAS_DESCONTO: dict[str, tuple[float, float]] = {
    "vip": (0.10, 0.15),
    "atacado": (0.05, 0.08),
}
TAXAS_PADRAO: tuple[float, float] = (0, 0.02)


def calcular_subtotal(itens: list[dict]) -> float:
    """Soma preco * qtd dos itens. ValueError se algum qtd < 0. Lista vazia -> 0."""
    subtotal: float = 0
    for item in itens:
        if item["qtd"] < 0:
            raise ValueError("qtd negativa")
        subtotal = subtotal + item["preco"] * item["qtd"]
    return subtotal


def calcular_desconto(subtotal: float, tipo_cliente: str) -> float:
    """Retorna o VALOR do desconto (não o total líquido) para o subtotal e o tipo de cliente."""
    try:
        taxa_normal, taxa_alta = TAXAS_DESCONTO.get(tipo_cliente, TAXAS_PADRAO)
    except TypeError:
        taxa_normal, taxa_alta = TAXAS_PADRAO
    taxa = taxa_alta if subtotal > LIMITE_FAIXA_ALTA else taxa_normal
    return subtotal * taxa


def formatar_relatorio(totais_por_cliente: dict[str, float]) -> str:
    """Gera o texto do relatório a partir do total líquido por cliente."""
    linhas: list[str] = []
    total_geral: float = 0
    for cliente in sorted(totais_por_cliente):
        valor = totais_por_cliente[cliente]
        linhas.append(cliente + ": " + ("%.2f" % valor))
        total_geral = total_geral + valor
    linhas.append("TOTAL: " + ("%.2f" % total_geral))
    return "\n".join(linhas)


def gerar_relatorio(pedidos: list[dict]) -> str:
    """Gera o relatório consolidado de vendas líquidas por cliente."""
    totais_por_cliente: dict[str, float] = {}
    for pedido in pedidos:
        cliente = pedido["cliente"]
        subtotal = calcular_subtotal(pedido["itens"])
        desconto = calcular_desconto(subtotal, pedido["tipo"])
        total_pedido = subtotal - desconto
        if cliente in totais_por_cliente:
            totais_por_cliente[cliente] = totais_por_cliente[cliente] + total_pedido
        else:
            totais_por_cliente[cliente] = total_pedido
    return formatar_relatorio(totais_por_cliente)
