LIMITE_FAIXA_ALTA = 1000
TAXAS_DESCONTO: dict[str, tuple[float, float]] = {
    "vip": (0.10, 0.15),
    "atacado": (0.05, 0.08),
}
TAXAS_PADRAO: tuple[float, float] = (0.0, 0.02)


def calcular_subtotal(itens: list[dict]) -> float:
    """Soma preco * qtd dos itens. ValueError se algum qtd < 0. Lista vazia -> 0."""
    total = 0
    for item in itens:
        if item["qtd"] < 0:
            raise ValueError("qtd negativa")
        total = total + item["preco"] * item["qtd"]
    return total


def calcular_desconto(subtotal: float, tipo_cliente: str) -> float:
    """Retorna o VALOR do desconto (não o total líquido) para o subtotal e o tipo de cliente."""
    taxas = TAXAS_PADRAO
    for nome, par in TAXAS_DESCONTO.items():
        if tipo_cliente == nome:
            taxas = par
            break
    taxa = taxas[1] if subtotal > LIMITE_FAIXA_ALTA else taxas[0]
    # Taxa zero segue `subtotal * 0` (inteiro), como no cálculo original:
    # `subtotal * 0.0` converteria inteiros enormes para float cedo demais.
    if taxa == 0:
        return subtotal * 0
    return subtotal * taxa


def formatar_relatorio(totais_por_cliente: dict[str, float]) -> str:
    """Gera o texto do relatório a partir do total líquido por cliente."""
    texto = ""
    total = 0
    for cliente in sorted(totais_por_cliente.keys()):
        texto = texto + cliente + ": " + ("%.2f" % totais_por_cliente[cliente]) + "\n"
        total = total + totais_por_cliente[cliente]
    texto = texto + "TOTAL: " + ("%.2f" % total)
    return texto


def gerar_relatorio(pedidos: list[dict]) -> str:
    totais: dict[str, float] = {}
    for pedido in pedidos:
        cliente = pedido["cliente"]
        subtotal = calcular_subtotal(pedido["itens"])
        liquido = subtotal - calcular_desconto(subtotal, pedido["tipo"])
        if cliente in totais:
            totais[cliente] = totais[cliente] + liquido
        else:
            totais[cliente] = liquido
    return formatar_relatorio(totais)
