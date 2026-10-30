"""Classificação determinística de mensagens, usando só a biblioteca padrão."""

import re
import unicodedata


def classificar_mensagem(texto: str) -> dict:
    """Retorna categoria, urgência literal e tamanho original da mensagem.

    As regras de categoria e sua prioridade estão em SUPOSICOES.md.
    Entradas que não sejam strings levantam TypeError.
    """
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma str")

    tamanho = len(texto)
    urgente = "URGENTE" in texto

    if texto == "":
        categoria = "vazia"
    else:
        simplificado = "".join(
            caractere
            for caractere in unicodedata.normalize("NFD", texto.casefold())
            if unicodedata.category(caractere) != "Mn"
        )
        palavras = set(re.findall(r"[^\W\d_]+", simplificado))

        if palavras & {"ruim", "pessimo", "problema", "defeito", "reclamacao"}:
            categoria = "reclamacao"
        elif "?" in texto or palavras & {
            "duvida", "como", "qual", "quando", "onde", "porque"
        }:
            categoria = "duvida"
        elif palavras & {"preciso", "solicito", "gostaria", "ajuda"}:
            categoria = "pedido"
        elif palavras & {"obrigado", "obrigada", "otimo", "excelente", "parabens"}:
            categoria = "elogio"
        else:
            categoria = "outro"

    return {"categoria": categoria, "urgente": urgente, "tamanho": tamanho}
