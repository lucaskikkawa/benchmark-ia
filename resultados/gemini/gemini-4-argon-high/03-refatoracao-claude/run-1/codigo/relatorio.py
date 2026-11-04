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
        subtotal += item["preco"] * quantidade
    return subtotal


def calcular_desconto(subtotal: float, tipo_cliente: str) -> float:
    """Retorna o VALOR do desconto (não o total líquido) para o subtotal e o tipo de cliente."""
    try:
        taxa_ate_limite, taxa_acima = TAXAS_DESCONTO.get(tipo_cliente, TAXAS_PADRAO)
    except TypeError:
        taxa_ate_limite, taxa_acima = TAXAS_PADRAO
    taxa = taxa_acima if subtotal > LIMITE_FAIXA_ALTA else taxa_ate_limite
    return subtotal * taxa


def formatar_relatorio(totais_por_cliente: dict[str, float]) -> str:
    """Gera o texto do relatório a partir do total líquido por cliente."""
    linhas = []
    total_geral = 0
    for cliente in sorted(totais_por_cliente.keys()):
        total_cliente = totais_por_cliente[cliente]
        linhas.append(f"{cliente:s}: {total_cliente:.2f}\n")
        total_geral += total_cliente
    linhas.append(f"TOTAL: {total_geral:.2f}")
    return "".join(linhas)


def gerar_relatorio(pedidos: list[dict]) -> str:
    """Calcula os totais líquidos por cliente a partir dos pedidos e formata o relatório."""
    totais_por_cliente: dict[str, float] = {}
    for pedido in pedidos:
        cliente = pedido["cliente"]
        subtotal = calcular_subtotal(pedido["itens"])
        desconto = calcular_desconto(subtotal, pedido["tipo"])
        total_liquido = subtotal - desconto
        if cliente in totais_por_cliente:
            totais_por_cliente[cliente] += total_liquido
        else:
            totais_por_cliente[cliente] = total_liquido
    return formatar_relatorio(totais_por_cliente)
