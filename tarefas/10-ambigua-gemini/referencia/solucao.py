def classificar_cliente(dados: dict) -> dict:
    """Calcula o score e determina a categoria do cliente."""
    cliente_id = dados["id"]
    nome = dados["nome"]
    compras = dados.get("compras", [])
    anos_ativo = int(dados.get("anos_ativo", 0))

    # Conforme premissa em SUPOSICOES.md: anos negativos são normalizados para 0
    anos_ativo = max(0, anos_ativo)

    # Conforme premissa em SUPOSICOES.md: valores negativos em compras são tratados
    # como devoluções e subtraídos da soma
    total_compras = sum(float(v) for v in compras)
    score_compras = total_compras * 0.1
    score_fidelidade = anos_ativo * 5.0
    score_total = round(score_compras + score_fidelidade, 2)

    # Faixas de categoria definidas em SUPOSICOES.md:
    if score_total >= 100.0:
        categoria = "Ouro"
    elif score_total >= 50.0:
        categoria = "Prata"
    else:
        categoria = "Bronze"

    return {
        "id": cliente_id,
        "nome": nome,
        "score": score_total,
        "categoria": categoria,
    }
