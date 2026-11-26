"""Classificador simples e puro de mensagens curtas."""

from __future__ import annotations

import re
import unicodedata

_RE_TEM_ALNUM = re.compile(r"[^\W_]", re.UNICODE)

_REGRAS_CATEGORIA: tuple[tuple[str, re.Pattern[str]], ...] = (
    (
        "reclamacao",
        re.compile(
            r"\b(?:"
            r"erro|erros|problema|problemas|falha|falhas|quebrou|defeito|"
            r"reclamacao|ruim|pessimo|pessima|horrivel|travou|bug|bugs|"
            r"atraso|atrasado|atrasada|nao\s+funciona|cobranca\s+indevida"
            r")\b"
        ),
    ),
    (
        "duvida",
        re.compile(
            r"\?|"
            r"\b(?:"
            r"duvida|duvidas|como|quando|onde|qual|quais|por\s+que|"
            r"ajuda|explica|explicar"
            r")\b"
        ),
    ),
    (
        "pedido",
        re.compile(
            r"\b(?:"
            r"por\s+favor|preciso|gostaria|solicito|quero|poderia|pode|"
            r"enviar|envie|cancelar|alterar|atualizar|agendar"
            r")\b"
        ),
    ),
    (
        "elogio",
        re.compile(
            r"\b(?:"
            r"obrigado|obrigada|parabens|excelente|otimo|otima|adorei|"
            r"perfeito|perfeita|maravilhoso|maravilhosa|valeu|"
            r"bom\s+trabalho|muito\s+bom"
            r")\b"
        ),
    ),
)


def _normalizar_para_categoria(texto: str) -> str:
    """Remove acentos (marcas combinantes) e aplica casefold sem codificar bytes."""
    decomposto = unicodedata.normalize("NFD", texto)
    sem_acentos = "".join(
        ch for ch in decomposto if unicodedata.category(ch) != "Mn"
    )
    return sem_acentos.casefold()


def _classificar_categoria(texto: str) -> str:
    if texto == "":
        return "vazia"

    normalizado = _normalizar_para_categoria(texto)
    if not _RE_TEM_ALNUM.search(normalizado):
        return "sem_conteudo"

    for categoria, padrao in _REGRAS_CATEGORIA:
        if padrao.search(normalizado):
            return categoria

    return "outro"


def classificar_mensagem(texto: str) -> dict[str, str | bool | int]:
    """Classifica uma mensagem curta de forma pura e determinística."""
    if not isinstance(texto, str):
        raise TypeError(
            f"texto deve ser str, recebido {type(texto).__name__}"
        )

    return {
        "categoria": _classificar_categoria(texto),
        "urgente": "URGENTE" in texto,
        "tamanho": len(texto),
    }
