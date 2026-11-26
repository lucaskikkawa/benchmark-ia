LIMITE_FAIXA_ALTA = 1000

TAXAS_DESCONTO: dict[str, tuple[float, float]] = {
    "vip": (0.10, 0.15),
    "atacado": (0.05, 0.08),
}

TAXAS_PADRAO: tuple[float, float] = (0.0, 0.02)


def calcular_subtotal(itens: list[dict]) -> float:
    """Soma preco * qtd dos itens. ValueError se algum qtd < 0. Lista vazia -> 0."""
    subtotal = 0
    for item in itens:
        quantidade = item["qtd"]
        if quantidade < 0:
            raise ValueError("qtd negativa")
        subtotal = subtotal + item["preco"] * quantidade
    return subtotal


def calcular_desconto(subtotal: float, tipo_cliente: str) -> float:
    """Retorna o valor do desconto (não o total líquido) para o subtotal e o tipo de cliente."""
    taxa_normal, taxa_faixa_alta = TAXAS_DESCONTO.get(tipo_cliente, TAXAS_PADRAO)
    taxa = taxa_faixa_alta if subtotal > LIMITE_FAIXA_ALTA else taxa_normal
    return subtotal * taxa


def formatar_relatorio(totais_por_cliente: dict[str, float]) -> str:
    """Gera o texto do relatório a partir do total líquido por cliente."""
    linhas: list[str] = []
    total_geral = 0
    for cliente in sorted(totais_por_cliente):
        total_cliente = totais_por_cliente[cliente]
        linhas.append(cliente + f": {total_cliente:.2f}")
        total_geral = total_geral + total_cliente
    linhas.append(f"TOTAL: {total_geral:.2f}")
    return "\n".join(linhas)


def gerar_relatorio(pedidos: list[dict]) -> str:
    """Calcula os totais líquidos por cliente e retorna o relatório formatado."""
    totais_por_cliente: dict[str, float] = {}
    for pedido in pedidos:
        cliente = pedido["cliente"]
        subtotal = calcular_subtotal(pedido["itens"])
        desconto = calcular_desconto(subtotal, pedido["tipo"])
        total_liquido = subtotal - desconto
        if cliente in totais_por_cliente:
            totais_por_cliente[cliente] = totais_por_cliente[cliente] + total_liquido
        else:
            totais_por_cliente[cliente] = total_liquido
    return formatar_relatorio(totais_por_cliente)
