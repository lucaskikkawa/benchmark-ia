import math


# Faixas de categoria: (limite inferior do score, nome da categoria).
# Ordenadas do maior para o menor; a primeira faixa atingida define a categoria.
FAIXAS_CATEGORIA = [
    (300, "Diamante"),
    (150, "Ouro"),
    (50, "Prata"),
    (0, "Bronze"),
]
CATEGORIA_PADRAO = "Bronze"  # usada para scores negativos (ver SUPOSICOES.md)


def classificar_cliente(dados: dict) -> dict:
    compras = dados.get("compras", [])
    anos_ativo = dados.get("anos_ativo", 0)

    # Anos negativos não fazem sentido: tratados como zero.
    anos_ativo = max(anos_ativo, 0)

    # fsum evita acúmulo de erro de ponto flutuante em listas grandes.
    # Não altera a lista original (apenas itera sobre ela).
    soma_compras = math.fsum(compras)

    score_base = soma_compras * 0.1
    score_fidelidade = anos_ativo * 5
    score = round(score_base + score_fidelidade, 2)

    return {
        "id": dados["id"],
        "nome": dados["nome"],
        "score": score,
        "categoria": _categoria_por_score(score),
    }


def _categoria_por_score(score: float) -> str:
    for limite, nome in FAIXAS_CATEGORIA:
        if score >= limite:
            return nome
    return CATEGORIA_PADRAO
