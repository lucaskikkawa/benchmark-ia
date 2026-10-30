"""Classificação de clientes por score de compras e fidelidade.

O contrato fechado está na especificação. As decisões sobre faixas de
categoria, valores negativos e campos extras estão em SUPOSICOES.md.
"""


def classificar_cliente(dados: dict) -> dict:
    """Calcula o score do cliente e devolve id, nome, score e categoria.

    Não altera ``dados`` nem a lista ``compras``.
    """
    soma_compras = sum(dados["compras"])
    score_compras = soma_compras * 0.1
    score_fidelidade = dados["anos_ativo"] * 5
    score = round(score_compras + score_fidelidade, 2)

    return {
        "id": dados["id"],
        "nome": dados["nome"],
        "score": score,
        "categoria": _categoria(score),
    }


def _categoria(score: float) -> str:
    """Segmento a partir do score já arredondado a 2 casas."""
    if score < 0:
        return "Crítico"
    if score < 50:
        return "Bronze"
    if score < 200:
        return "Prata"
    if score < 1000:
        return "Ouro"
    return "Platina"
