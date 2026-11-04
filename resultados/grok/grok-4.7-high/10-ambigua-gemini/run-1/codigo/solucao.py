"""Classificação de clientes por score de fidelidade.

O cálculo do score segue o núcleo da especificação. Faixas de categoria,
estornos e demais premissas estão em SUPOSICOES.md.
"""

# Limiares em ordem decrescente. A primeira faixa com score >= limiar vence.
# Score abaixo de zero não entra em nenhuma e cai em "em_risco".
_FAIXAS = (
    (2500.0, "diamante"),
    (1000.0, "platina"),
    (400.0, "ouro"),
    (150.0, "prata"),
    (50.0, "bronze"),
    (0.0, "iniciante"),
)


def classificar_cliente(dados: dict) -> dict:
    """Retorna id, nome, score e categoria sem alterar a entrada.

    score = round(soma(compras) * 0.1 + anos_ativo * 5, 2)
    """
    soma_compras = sum(dados["compras"])
    score = round(soma_compras * 0.1 + dados["anos_ativo"] * 5, 2)
    if score == 0:
        score = 0.0

    return {
        "id": dados["id"],
        "nome": dados["nome"],
        "score": score,
        "categoria": _categoria_do_score(score),
    }


def _categoria_do_score(score: float) -> str:
    for limiar, categoria in _FAIXAS:
        if score >= limiar:
            return categoria
    return "em_risco"
