"""Classificador determinístico de mensagens curtas."""

from __future__ import annotations

import unicodedata


_PALAVRAS_RECLAMACAO: tuple[str, ...] = (
    "erro",
    "problema",
    "defeito",
    "falha",
    "reclamacao",
    "reclamar",
    "ruim",
    "pessimo",
    "quebrado",
    "demora",
    "atraso",
)

_PALAVRAS_ELOGIO: tuple[str, ...] = (
    "parabens",
    "excelente",
    "otimo",
    "maravilhoso",
    "obrigado",
    "obrigada",
    "elogio",
    "perfeito",
    "adorei",
    "gostei",
)

_PALAVRAS_PEDIDO: tuple[str, ...] = (
    "solicito",
    "pedido",
    "favor",
    "preciso",
    "quero",
    "gostaria",
    "enviar",
    "cancelar",
)

_PALAVRAS_DUVIDA: tuple[str, ...] = (
    "como",
    "quando",
    "onde",
    "qual",
    "quais",
    "quem",
    "duvida",
    "poque",
    "por que",
    "porque",
)


def _normalizar_para_busca(texto: str) -> str:
    """Converte para minúsculas e remove diacríticos para comparação de categorias."""
    decomposto = unicodedata.normalize("NFD", texto.lower())
    return "".join(ch for ch in decomposto if unicodedata.category(ch) != "Mn")


def _extrair_palavras(texto_normalizado: str) -> set[str]:
    """Extrai tokens alfanuméricos do texto normalizado."""
    palavras: list[str] = []
    atual: list[str] = []
    for ch in texto_normalizado:
        if ch.isalnum():
            atual.append(ch)
        elif atual:
            palavras.append("".join(atual))
            atual = []
    if atual:
        palavras.append("".join(atual))
    return set(palavras)


def classificar_mensagem(texto: str) -> dict:
    """Classifica uma mensagem de texto em categoria, urgência e tamanho.

    Args:
        texto: A mensagem de entrada (deve ser exatamente do tipo `str`).

    Returns:
        Dicionário contendo `categoria` (str), `urgente` (bool) e `tamanho` (int).

    Raises:
        TypeError: Se `texto` não for uma instância de `str`.
    """
    if not isinstance(texto, str):
        raise TypeError(f"Esperado 'str', mas recebeu '{type(texto).__name__}'.")

    tamanho = len(texto)
    urgente = "URGENTE" in texto

    if texto == "":
        return {
            "categoria": "vazia",
            "urgente": False,
            "tamanho": 0,
        }

    normalizado = _normalizar_para_busca(texto)
    palavras = _extrair_palavras(normalizado)

    if not palavras:
        if "?" in texto:
            categoria = "duvida"
        else:
            categoria = "sem_conteudo"
    elif any(p in palavras for p in _PALAVRAS_RECLAMACAO):
        categoria = "reclamacao"
    elif "?" in texto or "por que" in normalizado or any(p in palavras for p in _PALAVRAS_DUVIDA):
        categoria = "duvida"
    elif any(p in palavras for p in _PALAVRAS_PEDIDO):
        categoria = "pedido"
    elif any(p in palavras for p in _PALAVRAS_ELOGIO):
        categoria = "elogio"
    else:
        categoria = "outro"

    return {
        "categoria": categoria,
        "urgente": urgente,
        "tamanho": tamanho,
    }
