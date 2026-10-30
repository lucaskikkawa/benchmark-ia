"""Classificação determinística e simples de mensagens curtas."""

import unicodedata


def _normalizar(texto: str) -> str:
    """Devolve uma forma sem acentos e em minúsculas para a classificação."""
    decomposed = unicodedata.normalize("NFD", texto).casefold()
    return "".join(
        caractere
        for caractere in decomposed
        if unicodedata.category(caractere) != "Mn"
    )


def classificar_mensagem(texto: str) -> dict:
    """Classifica uma mensagem e informa se contém o marcador URGENTE."""
    if not isinstance(texto, str):
        raise TypeError("texto deve ser str")

    tamanho = len(texto)
    urgente = "URGENTE" in texto

    if texto == "":
        return {"categoria": "vazia", "urgente": False, "tamanho": 0}

    normalizado = _normalizar(texto)
    palavras = set("".join(c if c.isalnum() else " " for c in normalizado).split())

    # A prioridade torna o resultado estável quando há sinais de mais de um tipo.
    if palavras & {"reclamo", "reclamar", "problema", "erro", "defeito", "insatisfeito", "ruim"}:
        categoria = "reclamacao"
    elif "?" in normalizado or palavras & {"como", "quando", "onde", "porque", "porquê", "qual", "duvida", "saber"}:
        categoria = "duvida"
    elif palavras & {"quero", "preciso", "solicito", "favor", "pedido", "envie", "enviar", "ajuda"}:
        categoria = "pedido"
    elif palavras & {"obrigado", "obrigada", "excelente", "otimo", "otima", "bom", "boa", "gostei", "adoro"}:
        categoria = "elogio"
    else:
        categoria = "outro"

    return {"categoria": categoria, "urgente": urgente, "tamanho": tamanho}
