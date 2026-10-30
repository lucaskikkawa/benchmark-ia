"""Classificação de clientes e cálculo de score de fidelidade.

As decisões de design para os pontos abertos da especificação estão
documentadas em SUPOSICOES.md.
"""

from numbers import Real

# Faixas de categoria: (score mínimo inclusivo, nome), da maior para a menor.
# Scores abaixo do menor limiar (inclusive negativos) caem em "Bronze".
FAIXAS_CATEGORIA = (
    (1000, "Diamante"),
    (500, "Ouro"),
    (100, "Prata"),
)
CATEGORIA_BASE = "Bronze"

PERCENTUAL_COMPRAS = 0.1
PONTOS_POR_ANO = 5


def _eh_numero(valor) -> bool:
    """Aceita int/float (e outros Real), mas rejeita bool."""
    return isinstance(valor, Real) and not isinstance(valor, bool)


def _validar(dados) -> None:
    if not isinstance(dados, dict):
        raise TypeError("dados deve ser um dict")

    for chave in ("id", "nome", "compras", "anos_ativo"):
        if chave not in dados:
            raise KeyError(f"campo obrigatório ausente: {chave!r}")

    if not isinstance(dados["id"], str):
        raise TypeError("'id' deve ser str")
    if not isinstance(dados["nome"], str):
        raise TypeError("'nome' deve ser str")

    compras = dados["compras"]
    if not isinstance(compras, (list, tuple)):
        raise TypeError("'compras' deve ser uma lista de números")
    for i, valor in enumerate(compras):
        if not _eh_numero(valor):
            raise TypeError(f"'compras[{i}]' deve ser int ou float")
        if valor != valor or valor in (float("inf"), float("-inf")):
            raise ValueError(f"'compras[{i}]' deve ser um número finito")

    anos = dados["anos_ativo"]
    if not isinstance(anos, int) or isinstance(anos, bool):
        raise TypeError("'anos_ativo' deve ser int")


def _categorizar(score) -> str:
    for minimo, nome in FAIXAS_CATEGORIA:
        if score >= minimo:
            return nome
    return CATEGORIA_BASE


def classificar_cliente(dados: dict) -> dict:
    """Calcula o score de fidelidade e a categoria de um cliente.

    score = round(soma(compras) * 0.1 + max(anos_ativo, 0) * 5, 2)

    Valores negativos em `compras` são tratados como estornos/devoluções
    e entram na soma (abatendo o total). `anos_ativo` negativo é tratado
    como 0. Campos extras na entrada são ignorados. A entrada nunca é
    modificada.
    """
    _validar(dados)

    # sum() percorre a lista sem copiá-la nem alterá-la: O(n) e sem
    # efeitos colaterais, adequado para grandes volumes de compras.
    soma_compras = sum(dados["compras"])
    anos_ativo = max(dados["anos_ativo"], 0)

    score = round(soma_compras * PERCENTUAL_COMPRAS + anos_ativo * PONTOS_POR_ANO, 2)

    return {
        "id": dados["id"],
        "nome": dados["nome"],
        "score": score,
        "categoria": _categorizar(score),
    }
