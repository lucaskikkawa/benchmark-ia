"""Relatório de vendas líquidas por cliente."""

LIMITE_FAIXA_ALTA = 1000

# tipo de cliente -> (taxa até o limite, taxa acima do limite)
TAXAS_DESCONTO: dict[str, tuple[float, float]] = {
    "vip": (0.10, 0.15),
    "atacado": (0.05, 0.08),
}
# Tipos não listados em TAXAS_DESCONTO.
TAXAS_PADRAO: tuple[float, float] = (0, 0.02)


def calcular_subtotal(itens: list[dict]) -> float:
    """Soma preco * qtd dos itens. ValueError se algum qtd < 0. Lista vazia -> 0.

    Cada item é validado antes de ler o preço, como no código original
    (isso define qual exceção aparece primeiro em itens malformados).
    """
    subtotal = 0
    for item in itens:
        if item["qtd"] < 0:
            raise ValueError("qtd negativa")
        subtotal = subtotal + item["preco"] * item["qtd"]
    return subtotal


def calcular_desconto(subtotal: float, tipo_cliente: str) -> float:
    """Retorna o valor do desconto aplicável ao subtotal para o tipo de cliente."""
    taxa_normal, taxa_alta = TAXAS_DESCONTO.get(tipo_cliente, TAXAS_PADRAO)
    taxa = taxa_alta if subtotal > LIMITE_FAIXA_ALTA else taxa_normal
    return subtotal * taxa


def formatar_relatorio(totais_por_cliente: dict[str, float]) -> str:
    """Uma linha "cliente: valor" por cliente (ordem alfabética) e a linha final TOTAL."""
    linhas = []
    # Soma sequencial na ordem das linhas (não sum(): a ordem e o modo de somar
    # floats mudam o arredondamento do total em relação ao original).
    total_geral = 0
    for cliente in sorted(totais_por_cliente):
        total = totais_por_cliente[cliente]
        linhas.append(f"{cliente}: {total:.2f}")
        total_geral = total_geral + total
    linhas.append(f"TOTAL: {total_geral:.2f}")
    return "\n".join(linhas)


def gerar_relatorio(pedidos: list[dict]) -> str:
    """Agrupa os pedidos por cliente, aplica descontos e formata o relatório."""
    totais: dict[str, float] = {}
    for pedido in pedidos:
        # Mesma ordem de acesso do original: cliente, itens, tipo.
        cliente = pedido["cliente"]
        subtotal = calcular_subtotal(pedido["itens"])
        liquido = subtotal - calcular_desconto(subtotal, pedido["tipo"])
        totais[cliente] = totais[cliente] + liquido if cliente in totais else liquido
    return formatar_relatorio(totais)
