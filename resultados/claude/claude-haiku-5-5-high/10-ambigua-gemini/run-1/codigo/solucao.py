"""Classificação de clientes e score de fidelidade.

Regras do núcleo explícito:
    score = soma(compras) * 0.1 + anos_ativo * 5, arredondado para 2 casas.

As decisões sobre os pontos em aberto (faixas de categoria, estornos,
anos negativos, campos extras) estão documentadas em SUPOSICOES.md.
"""

# Faixas de categoria: (score mínimo inclusivo, nome da categoria).
# Ordenadas do maior para o menor limite; a primeira faixa atendida vence.
CATEGORIAS = (
    (600, "Platina"),
    (300, "Ouro"),
    (100, "Prata"),
    (float("-inf"), "Bronze"),
)


def classificar_cliente(dados: dict) -> dict:
    """Calcula o score de fidelidade e a categoria de um cliente.

    Não modifica `dados` nem a lista `compras` contida nele. Campos extras
    da entrada são ignorados e não aparecem no retorno.
    """
    compras = dados.get("compras") or []
    anos_ativo = dados.get("anos_ativo") or 0

    # Anos negativos não fazem sentido como tempo de atividade: tratados como 0.
    anos_ativo = max(anos_ativo, 0)

    # sum() não altera a lista; a soma inclui estornos (valores negativos).
    score_compras = sum(compras) * 0.1
    score_fidelidade = anos_ativo * 5
    score = round(score_compras + score_fidelidade, 2)

    return {
        "id": dados["id"],
        "nome": dados["nome"],
        "score": score,
        "categoria": _categoria_por_score(score),
    }


def _categoria_por_score(score: float) -> str:
    for limite, nome in CATEGORIAS:
        if score >= limite:
            return nome
    # Inalcançável: o último limite é -infinito. Mantido por segurança.
    return CATEGORIAS[-1][1]
