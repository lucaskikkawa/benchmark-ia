"""Cálculo do score e classificação de clientes por fidelidade."""


def classificar_cliente(dados: dict) -> dict:
    """Retorna identificação, score arredondado e categoria sem alterar dados.

    As premissas de entrada e as faixas estão descritas em SUPOSICOES.md.
    """
    score = round(sum(dados["compras"]) * 0.1 + dados["anos_ativo"] * 5, 2)

    if score < 100:
        categoria = "Bronze"
    elif score < 500:
        categoria = "Prata"
    elif score < 1000:
        categoria = "Ouro"
    else:
        categoria = "Diamante"

    return {
        "id": dados["id"],
        "nome": dados["nome"],
        "score": score,
        "categoria": categoria,
    }
