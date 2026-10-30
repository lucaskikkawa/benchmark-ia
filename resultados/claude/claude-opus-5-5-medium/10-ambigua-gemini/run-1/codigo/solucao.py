"""Classificação de clientes e cálculo de score de fidelidade.

Decisões de design para os pontos abertos estão documentadas em SUPOSICOES.md.
"""

from numbers import Real

# Faixas de categoria: (limite inferior inclusivo do score, nome), em ordem decrescente.
FAIXAS_CATEGORIA = (
    (1000.0, "Diamante"),
    (500.0, "Ouro"),
    (100.0, "Prata"),
    (0.0, "Bronze"),
)
CATEGORIA_PADRAO = "Bronze"

PERCENTUAL_COMPRAS = 0.1
PONTOS_POR_ANO = 5


def _eh_numero(valor) -> bool:
    # bool é subclasse de int, mas não representa um valor monetário.
    return isinstance(valor, Real) and not isinstance(valor, bool)


def _categorizar(score: float) -> str:
    for limite, nome in FAIXAS_CATEGORIA:
        if score >= limite:
            return nome
    return CATEGORIA_PADRAO


def classificar_cliente(dados: dict) -> dict:
    if not isinstance(dados, dict):
        raise TypeError("dados deve ser um dict")

    compras = dados.get("compras") or []
    if not isinstance(compras, (list, tuple)):
        raise TypeError("compras deve ser uma lista de números")
    for valor in compras:
        if not _eh_numero(valor):
            raise TypeError(f"valor de compra inválido: {valor!r}")

    anos_ativo = dados.get("anos_ativo", 0) or 0
    if not _eh_numero(anos_ativo):
        raise TypeError(f"anos_ativo inválido: {anos_ativo!r}")

    # Valores negativos são estornos/devoluções e abatem a soma (sem alterar a lista).
    soma_compras = sum(compras)
    # Anos ativos negativos não têm significado: considerados como 0.
    anos_ativo = max(anos_ativo, 0)

    score = round(soma_compras * PERCENTUAL_COMPRAS + anos_ativo * PONTOS_POR_ANO, 2)

    return {
        "id": dados.get("id"),
        "nome": dados.get("nome"),
        "score": score,
        "categoria": _categorizar(score),
    }
