def classificar_cliente(dados: dict) -> dict:
    """Calcula o score de compras e fidelidade e atribui uma categoria.

    A entrada é somente lida; nenhum dos seus campos é alterado.
    """
    compras = dados["compras"]
    soma_compras = sum(compras)
    anos_ativo = max(0, dados["anos_ativo"])

    score = round(soma_compras * 0.1 + anos_ativo * 5, 2)

    # Faixas crescentes e não sobrepostas; scores negativos permanecem na
    # categoria inicial, pois podem resultar de estornos superiores às compras.
    if score < 100:
        categoria = "Bronze"
    elif score < 500:
        categoria = "Prata"
    elif score < 1000:
        categoria = "Ouro"
    else:
        categoria = "Platina"

    return {
        "id": dados["id"],
        "nome": dados["nome"],
        "score": score,
        "categoria": categoria,
    }
