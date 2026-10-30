"""Classificação de clientes pelo histórico de compras e tempo de atividade."""


def classificar_cliente(dados: dict) -> dict:
    """Calcula o score e atribui uma categoria sem alterar os dados de entrada.

    Espera que ``dados`` contenha ``id``, ``nome``, ``compras`` e
    ``anos_ativo`` nos tipos descritos no enunciado.
    """
    score_compras = sum(dados["compras"]) * 0.1
    score_fidelidade = dados["anos_ativo"] * 5
    score = round(score_compras + score_fidelidade, 2)

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
