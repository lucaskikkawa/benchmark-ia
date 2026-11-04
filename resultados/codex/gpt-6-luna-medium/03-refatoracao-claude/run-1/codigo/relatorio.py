LIMITE_FAIXA_ALTA = 1000
TAXAS_DESCONTO: dict[str, tuple[float, float]] = {
    "vip": (0.10, 0.15),
    "atacado": (0.05, 0.08),
}
TAXAS_PADRAO: tuple[float, float] = (0.0, 0.02)


def calcular_subtotal(itens: list[dict]) -> float:
    """Soma preco * qtd dos itens. ValueError se algum qtd < 0."""
    subtotal = 0
    for item in itens:
        if item["qtd"] < 0:
            raise ValueError("qtd negativa")
        subtotal = subtotal + item["preco"] * item["qtd"]
    return subtotal


def calcular_desconto(subtotal: float, tipo_cliente: str) -> float:
    """Retorna o valor do desconto para o subtotal e o tipo de cliente."""
    if tipo_cliente == "vip":
        taxas = TAXAS_DESCONTO.get("vip", TAXAS_PADRAO)
    elif tipo_cliente == "atacado":
        taxas = TAXAS_DESCONTO.get("atacado", TAXAS_PADRAO)
    else:
        taxas = TAXAS_PADRAO
    taxa = taxas[1] if subtotal > LIMITE_FAIXA_ALTA else taxas[0]
    return subtotal * taxa


def formatar_relatorio(totais_por_cliente: dict[str, float]) -> str:
    """Gera o texto do relatório a partir do total líquido por cliente."""
    relatorio = ""
    total = 0
    for cliente in sorted(totais_por_cliente.keys()):
        relatorio = relatorio + cliente + ": " + ("%.2f" % totais_por_cliente[cliente]) + "\n"
        total = total + totais_por_cliente[cliente]
    relatorio = relatorio + "TOTAL: " + ("%.2f" % total)
    return relatorio


def gerar_relatorio(pedidos: list[dict]) -> str:
    totais_por_cliente = {}
    for pedido in pedidos:
        cliente = pedido["cliente"]
        subtotal = calcular_subtotal(pedido["itens"])
        tipo_cliente = pedido["tipo"]
        desconto = calcular_desconto(subtotal, tipo_cliente)
        total_liquido = subtotal - desconto

        if cliente in totais_por_cliente:
            totais_por_cliente[cliente] = totais_por_cliente[cliente] + total_liquido
        else:
            totais_por_cliente[cliente] = total_liquido
    return formatar_relatorio(totais_por_cliente)
