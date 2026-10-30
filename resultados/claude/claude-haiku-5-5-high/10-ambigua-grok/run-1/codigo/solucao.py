"""Classificação de mensagens curtas. Usa apenas a biblioteca padrão.

A função é pura: não lê arquivos, relógio ou rede. Ver SUPOSICOES.md para as
decisões tomadas nos pontos em aberto.
"""

import re
import unicodedata

CATEGORIA_VAZIA = "vazia"
CATEGORIA_INDEFINIDA = "indefinida"
CATEGORIA_PADRAO = "outro"

# Ordem de prioridade: quando mais de uma categoria casa, vence a primeira.
# Os padrões são aplicados ao texto sem acentos e em minúsculas.
_REGRAS = (
    (
        "reclamacao",
        re.compile(
            r"\b(reclam|problema|defeito|nao\s+funciona|pessimo|horrivel"
            r"|insatisf|cobrad[oa]\s+indevid)"
        ),
    ),
    (
        "pedido",
        re.compile(r"\b(quero|preciso|solicit|peco|envi|gostaria|por\s+favor)"),
    ),
    (
        "duvida",
        re.compile(r"\?|\b(duvida|pergunta|como|qual|quando|onde)\b"),
    ),
    (
        "elogio",
        re.compile(
            r"\b(obrigad|parabens|excelente|otimo|adorei|gostei|maravilh"
            r"|recomendo)"
        ),
    ),
)


def _normalizar_para_categoria(texto: str) -> str:
    # Só para a categoria. A regra de "URGENTE" usa o texto original.
    decomposto = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(c for c in decomposto if not unicodedata.combining(c))
    return sem_acentos.casefold()


def _categoria(texto: str) -> str:
    if not any(c.isalnum() for c in texto):
        return CATEGORIA_INDEFINIDA
    normalizado = _normalizar_para_categoria(texto)
    for nome, padrao in _REGRAS:
        if padrao.search(normalizado):
            return nome
    return CATEGORIA_PADRAO


def classificar_mensagem(texto: str) -> dict:
    """Devolve categoria, urgência e tamanho de uma mensagem.

    - ``tamanho`` é ``len(texto)`` em code points, sem alterar o texto.
    - ``urgente`` é True quando a substring ``"URGENTE"`` aparece no texto.
    - ``categoria`` é ``"vazia"`` só para a string vazia.

    Levanta ``TypeError`` se ``texto`` não for ``str``.
    """
    if not isinstance(texto, str):
        raise TypeError(f"texto deve ser str, não {type(texto).__name__}")

    if texto == "":
        return {"categoria": CATEGORIA_VAZIA, "urgente": False, "tamanho": 0}

    return {
        "categoria": _categoria(texto),
        "urgente": "URGENTE" in texto,
        "tamanho": len(texto),
    }
