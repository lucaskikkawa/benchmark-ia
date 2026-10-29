"""Classificação heurística de uma mensagem curta."""

_REGRAS = (
    ("reclamacao", ("reclam", "péssim", "pessimo", "insatisfeit", "horrív", "horriv")),
    ("duvida", ("?", "como ", "dúvid", "duvid")),
    ("elogio", ("obrigad", "ótim", "otimo", "excelente", "parabén", "paraben")),
    ("pedido", ("quero", "preciso", "solicito", "favor")),
)


def classificar_mensagem(texto: str) -> dict:
    """Classifica texto. Só a string vazia usa a categoria 'vazia'.

    urgente é True quando a substring URGENTE aparece. tamanho é len(texto).
    A categoria dos demais textos segue a tabela documentada em SUPOSICOES.md.
    """
    if not isinstance(texto, str):
        raise TypeError("texto deve ser str")
    if texto == "":
        categoria = "vazia"
    else:
        categoria = _categoria(texto)
    return {
        "categoria": categoria,
        "urgente": "URGENTE" in texto,
        "tamanho": len(texto),
    }


def _categoria(texto: str) -> str:
    base = texto.casefold()
    for nome, sinais in _REGRAS:
        if any(sinal in base for sinal in sinais):
            return nome
    return "outro"
