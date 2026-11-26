"""Classificador simples de mensagens curtas usando apenas a biblioteca padrão."""

import re
import unicodedata

_REGRAS_CATEGORIA: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "reclamacao",
        (
            "reclamacao",
            "reclamar",
            "problema",
            "erro",
            "defeito",
            "quebrado",
            "ruim",
            "pessimo",
            "horrivel",
            "atraso",
            "insatisfeito",
            "cancelar",
            "devolucao",
        ),
    ),
    (
        "pedido",
        (
            "solicito",
            "preciso",
            "gostaria",
            "quero",
            "envie",
            "enviar",
            "mande",
            "atualizar",
            "alterar",
            "pedir",
            "favor",
        ),
    ),
    (
        "duvida",
        (
            "duvida",
            "pergunta",
            "como",
            "quando",
            "onde",
            "qual",
            "quais",
            "porque",
            "saber",
            "funciona",
        ),
    ),
    (
        "elogio",
        (
            "parabens",
            "obrigado",
            "obrigada",
            "excelente",
            "otimo",
            "maravilhoso",
            "adorei",
            "gostei",
            "perfeito",
            "incrivel",
            "bom",
        ),
    ),
)

_PADROES_CATEGORIA: tuple[tuple[str, re.Pattern[str]], ...] = tuple(
    (
        categoria,
        re.compile(r"\b(?:" + "|".join(re.escape(p) for p in palavras) + r")\b"),
    )
    for categoria, palavras in _REGRAS_CATEGORIA
)


def _normalizar_para_busca(texto: str) -> str:
    """Remove acentos e aplica casefold apenas para classificação de categoria."""
    sem_acentos = "".join(
        ch for ch in unicodedata.normalize("NFD", texto) if unicodedata.category(ch) != "Mn"
    )
    return sem_acentos.casefold()


def _escolher_categoria(texto: str) -> str:
    if texto == "":
        return "vazia"

    normalizado = _normalizar_para_busca(texto)
    if not any(ch.isalnum() for ch in normalizado):
        return "sem_palavras"

    for categoria, padrao in _PADROES_CATEGORIA:
        if padrao.search(normalizado):
            return categoria
        if categoria == "duvida" and "?" in texto:
            return "duvida"

    return "outro"


def classificar_mensagem(texto: str) -> dict:
    """Classifica uma mensagem curta e retorna categoria, urgência e tamanho."""
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma instância de str")

    return {
        "categoria": _escolher_categoria(texto),
        "urgente": "URGENTE" in texto,
        "tamanho": len(texto),
    }
