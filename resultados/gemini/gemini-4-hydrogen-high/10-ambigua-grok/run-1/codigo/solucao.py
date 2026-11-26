"""Classificador deterministico de mensagens curtas."""

from __future__ import annotations

import re
import unicodedata

_REGRAS_CATEGORIAS: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "reclamacao",
        (
            "erro",
            "problema",
            "defeito",
            "quebrado",
            "quebrada",
            "falha",
            "lento",
            "lenta",
            "horrivel",
            "pessimo",
            "pessima",
            "nao funciona",
            "reclamacao",
            "reclamar",
            "atraso",
            "atrasado",
            "atrasada",
            "cobranca indevida",
            "cancelar",
            "insatisfeito",
            "insatisfeita",
        ),
    ),
    (
        "pedido",
        (
            "por favor",
            "preciso",
            "gostaria",
            "quero",
            "solicito",
            "solicitacao",
            "enviar",
            "envie",
            "mandar",
            "mande",
            "atualizar",
            "atualize",
            "alterar",
            "altere",
            "ajuda",
            "ajudar",
            "ajude",
            "suporte",
            "pedido",
        ),
    ),
    (
        "duvida",
        (
            "como",
            "quando",
            "onde",
            "qual",
            "quais",
            "porque",
            "por que",
            "duvida",
            "duvidas",
            "funciona",
            "explica",
            "explicar",
            "entender",
            "posso",
            "consigo",
        ),
    ),
    (
        "elogio",
        (
            "obrigado",
            "obrigada",
            "parabens",
            "excelente",
            "otimo",
            "otima",
            "maravilhoso",
            "maravilhosa",
            "perfeito",
            "perfeita",
            "adorei",
            "gostei",
            "elogio",
            "recomendo",
            "valeu",
        ),
    ),
)

_PADROES_CATEGORIAS: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (
        categoria,
        re.compile(
            r"\b(?:" + "|".join(re.escape(termo) for termo in termos) + r")\b"
        ),
    )
    for categoria, termos in _REGRAS_CATEGORIAS
)


def _normalizar_para_categoria(texto: str) -> str:
    """Remove acentos e converte para minusculas apenas para classificar a categoria."""
    decomposed = unicodedata.normalize("NFD", texto)
    sem_acentos = "".join(ch for ch in decomposed if not unicodedata.combining(ch))
    return sem_acentos.lower()


def _escolher_categoria(texto_normalizado: str) -> str:
    """Determina a categoria de um texto nao vazio ja normalizado."""
    for categoria, padrao in _PADROES_CATEGORIAS:
        if categoria == "duvida" and "?" in texto_normalizado:
            return "duvida"
        if padrao.search(texto_normalizado):
            return categoria

    if not any(ch.isalnum() for ch in texto_normalizado):
        return "sem_conteudo"

    return "outro"


def classificar_mensagem(texto: str) -> dict:
    """Classifica uma mensagem curta em categoria, urgencia e tamanho."""
    if not isinstance(texto, str):
        raise TypeError(f"texto deve ser str, recebido {type(texto).__name__}")

    tamanho = len(texto)
    if tamanho == 0:
        return {
            "categoria": "vazia",
            "urgente": False,
            "tamanho": 0,
        }

    urgente = "URGENTE" in texto
    normalizado = _normalizar_para_categoria(texto)
    categoria = _escolher_categoria(normalizado)

    return {
        "categoria": categoria,
        "urgente": urgente,
        "tamanho": tamanho,
    }
