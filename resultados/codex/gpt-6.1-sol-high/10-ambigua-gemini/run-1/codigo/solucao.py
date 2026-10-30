"""Cálculo do score de fidelidade e classificação de clientes."""


def classificar_cliente(dados: dict) -> dict:
    """Retorna os dados de classificação sem modificar a entrada.

    As faixas e as premissas de entrada estão descritas em SUPOSICOES.md.
    """
    soma_compras = sum(dados["compras"])
    score = round(soma_compras * 0.1 + dados["anos_ativo"] * 5, 2)

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
