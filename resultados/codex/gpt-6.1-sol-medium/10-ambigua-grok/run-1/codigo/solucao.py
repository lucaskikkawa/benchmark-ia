"""Classificação determinística de mensagens curtas, sem dependências externas."""


def classificar_mensagem(texto: str) -> dict:
    """Classifica pelo sinal de pergunta, preservando o texto nas demais regras.

    Levanta TypeError quando o argumento não é uma string.
    """
    if not isinstance(texto, str):
        raise TypeError("texto deve ser str")

    if texto == "":
        categoria = "vazia"
    elif "?" in texto:
        categoria = "pergunta"
    else:
        categoria = "outro"

    return {
        "categoria": categoria,
        "urgente": "URGENTE" in texto,
        "tamanho": len(texto),
    }
