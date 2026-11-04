"""Classificação de mensagens curtas. Só biblioteca padrão, sem efeitos colaterais."""

import unicodedata

# Ordem de prioridade: quando mais de uma categoria casa, vence a primeira.
_PALAVRAS_POR_CATEGORIA = (
    ("reclamacao", ("reclamar", "reclamacao", "pessimo", "horrivel", "ruim", "problema", "erro", "demora", "defeito")),
    ("pedido", ("quero", "preciso", "gostaria", "por favor", "pode me", "poderia", "solicito")),
    ("duvida", ("?", "duvida", "como ", "por que", "porque", "o que", "quando")),
    ("elogio", ("obrigado", "obrigada", "parabens", "otimo", "excelente", "maravilhoso", "adorei")),
)
_CATEGORIA_PADRAO = "outro"
_CATEGORIA_SEM_PALAVRAS = "sem_palavras"


def _normalizar_para_categoria(texto: str) -> str:
    # Só usado na classificação: ignora caixa e acentos. Não afeta "urgente".
    decomposto = unicodedata.normalize("NFKD", texto.casefold())
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def classificar_mensagem(texto: str) -> dict:
    if not isinstance(texto, str):
        raise TypeError("texto deve ser str")

    resultado = {
        "categoria": "vazia",
        "urgente": "URGENTE" in texto,
        "tamanho": len(texto),
    }
    if texto == "":
        return resultado

    if not any(c.isalnum() for c in texto):
        resultado["categoria"] = _CATEGORIA_SEM_PALAVRAS
        return resultado

    normalizado = _normalizar_para_categoria(texto)
    for categoria, palavras in _PALAVRAS_POR_CATEGORIA:
        if any(p in normalizado for p in palavras):
            resultado["categoria"] = categoria
            return resultado

    resultado["categoria"] = _CATEGORIA_PADRAO
    return resultado
