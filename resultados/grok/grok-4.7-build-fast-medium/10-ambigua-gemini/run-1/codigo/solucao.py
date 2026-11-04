"""Classificação de clientes e score de fidelidade.

O score segue o núcleo fechado da especificação. Faixas de categoria,
tratamento de valores atípicos e o contrato de saída estão descritos em
SUPOSICOES.md.
"""

from __future__ import annotations

import math

# Limites inferiores inclusivos, avaliados do maior para o menor.
# A categoria usa o score já arredondado para as duas casas devolvidas.
_FAIXAS: tuple[tuple[float, str], ...] = (
    (3000.0, "diamante"),
    (1000.0, "platina"),
    (350.0, "ouro"),
    (100.0, "prata"),
    (0.0, "bronze"),
)


def _numero_real(valor: object, campo: str) -> int | float:
    """Aceita int e float finitos. Rejeita bool (subclasse de int) e não numéricos."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise TypeError(f"{campo} deve ser int ou float")
    if isinstance(valor, float) and not math.isfinite(valor):
        raise ValueError(f"{campo} deve ser um número finito")
    return valor


def _categoria(score: float) -> str:
    if score < 0:
        return "critico"
    for limite, nome in _FAIXAS:
        if score >= limite:
            return nome
    return "bronze"


def classificar_cliente(dados: dict) -> dict:
    """Calcula o score de fidelidade e a categoria do cliente.

    Não altera `dados` nem a lista `compras`. Campos além de id, nome,
    compras e anos_ativo são ignorados. O retorno tem exatamente as chaves
    id, nome, score e categoria.
    """
    if not isinstance(dados, dict):
        raise TypeError("dados deve ser um dicionário")

    cliente_id = dados["id"]
    nome = dados["nome"]
    compras = dados["compras"]
    anos_ativo = dados["anos_ativo"]

    if isinstance(compras, (str, bytes)) or not isinstance(compras, (list, tuple)):
        raise TypeError("compras deve ser uma lista de números")

    soma_compras = 0.0
    for indice, valor in enumerate(compras):
        soma_compras += _numero_real(valor, f"compras[{indice}]")

    anos = _numero_real(anos_ativo, "anos_ativo")
    score = round(soma_compras * 0.1 + anos * 5, 2)

    return {
        "id": cliente_id,
        "nome": nome,
        "score": score,
        "categoria": _categoria(score),
    }
