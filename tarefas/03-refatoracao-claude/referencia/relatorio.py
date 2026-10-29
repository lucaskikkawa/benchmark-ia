"""Relatório de vendas líquidas por cliente."""

LIMITE_FAIXA_ALTA = 1000

# tipo de cliente -> (taxa até o limite, taxa acima do limite)
TAXAS_DESCONTO: dict[str, tuple[float, float]] = {
    "vip": (0.10, 0.15),
    "atacado": (0.05, 0.08),
}
TAXAS_PADRAO = (0.0, 0.02)


def calcular_subtotal(itens: list[dict]) -> float:
    """Soma preco * qtd dos itens. ValueError se algum qtd < 0. Lista vazia -> 0."""
    subtotal = 0
    for item in itens:
        if item["qtd"] < 0:
            raise ValueError("qtd negativa")
        subtotal += item["preco"] * item["qtd"]
    return subtotal


def calcular_desconto(subtotal: float, tipo_cliente: str) -> float:
    """Retorna o valor do desconto aplicável ao subtotal para o tipo de cliente."""
    taxa_normal, taxa_alta = TAXAS_DESCONTO.get(tipo_cliente, TAXAS_PADRAO)
    taxa = taxa_alta if subtotal > LIMITE_FAIXA_ALTA else taxa_normal
    return subtotal * taxa


def formatar_relatorio(totais_por_cliente: dict[str, float]) -> str:
    """Uma linha "cliente: valor" por cliente (ordem alfabética) e a linha final TOTAL."""
    linhas = [f"{cliente}: {total:.2f}" for cliente, total in sorted(totais_por_cliente.items())]
    # Soma na mesma ordem das linhas para manter o arredondamento idêntico ao original.
    total_geral = sum(total for _, total in sorted(totais_por_cliente.items()))
    linhas.append(f"TOTAL: {total_geral:.2f}")
    return "\n".join(linhas)


def gerar_relatorio(pedidos: list[dict]) -> str:
    """Agrupa os pedidos por cliente, aplica descontos e formata o relatório."""
    totais: dict[str, float] = {}
    for pedido in pedidos:
        subtotal = calcular_subtotal(pedido["itens"])
        liquido = subtotal - calcular_desconto(subtotal, pedido["tipo"])
        totais[pedido["cliente"]] = totais.get(pedido["cliente"], 0) + liquido
    return formatar_relatorio(totais)
