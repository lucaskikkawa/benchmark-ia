def classificar_mensagem(texto: str) -> dict:
    """Classifica uma mensagem curta com regras determinísticas e locais."""
    if not isinstance(texto, str):
        raise TypeError("texto deve ser str")

    tamanho = len(texto)
    urgente = "URGENTE" in texto

    if texto == "":
        categoria = "vazia"
    else:
        # A classificação ignora diferenças entre maiúsculas e minúsculas,
        # mas mantém acentos e não altera a regra literal de urgência.
        normalizado = texto.lower()
        regras = (
            ("reclamacao", ("problema", "reclama", "defeito", "ruim", "insatisfeit")),
            ("duvida", ("?", "como", "qual", "quando", "onde", "por que", "dúvida")),
            ("elogio", ("obrigad", "ótimo", "otimo", "excelente", "parabéns", "gostei")),
            ("pedido", ("preciso", "por favor", "solicito", "quero", "poderia", "envie")),
        )
        categoria = "outro"
        for nome, termos in regras:
            if any(termo in normalizado for termo in termos):
                categoria = nome
                break

    return {"categoria": categoria, "urgente": urgente, "tamanho": tamanho}
