"""Módulo de classificação de mensagens curtas."""

import re

# Tabela de mapeamento para remoção de acentos básicos sem depender de
# unicodedata.normalize (que levanta UnicodeEncodeError com surrogates isolados como \ud800).
_ACCENT_MAP = str.maketrans(
    "áàâãäéèêëíìîïóòôõöúùûüçñÁÀÂÃÄÉÈÊËÍÌÎÏÓÒÔÕÖÚÙÛÜÇÑ",
    "aaaaaeeeeiiiiooooouuuucnAAAAAEEEEIIIIOOOOOUUUUCN",
)

_PALAVRAS_RECLAMACAO = {
    "defeito", "problema", "quebrado", "ruim", "pessimo", "erro",
    "reclamacao", "falha", "insatisfeito", "horrivel", "pior",
    "cancelar", "atraso", "estragado", "prejuizo", "estorno",
}

_EXPRESSOES_RECLAMACAO = (
    "nao funciona",
    "nao gostei",
    "veio quebrado",
    "veio errado",
)

_PALAVRAS_DUVIDA = {
    "como", "quando", "onde", "porque", "qual", "quem", "duvida",
    "ajuda", "saber", "funciona", "horario", "preco", "valor",
}

_EXPRESSOES_DUVIDA = (
    "por que",
    "como faco",
    "como funciona",
    "quanto custa",
)

_PALAVRAS_PEDIDO = {
    "solicito", "comprar", "pedido", "gostaria", "quero", "enviar",
    "preciso", "encomenda", "adquirir", "contratar", "solicitacao",
}

_PALAVRAS_ELOGIO = {
    "obrigado", "obrigada", "parabens", "otimo", "excelente", "bom",
    "boa", "perfeito", "maravilhoso", "adorei", "show", "agradeco",
}


def classificar_mensagem(texto: str) -> dict:
    """Classifica uma mensagem curta retornando um dicionário com os metadados.

    Args:
        texto: A mensagem em formato str a ser classificada.

    Returns:
        Um dict contendo ao menos:
            - categoria (str): Categoria atribuída ao texto.
            - urgente (bool): True se a substring "URGENTE" estiver presente.
            - tamanho (int): Quantidade de code points em texto.

    Raises:
        TypeError: Se texto não for uma instância de str.
    """
    if not isinstance(texto, str):
        raise TypeError(f"Esperado texto do tipo str, recebido: {type(texto).__name__}")

    tamanho = len(texto)
    urgente = "URGENTE" in texto

    if texto == "":
        return {
            "categoria": "vazia",
            "urgente": urgente,
            "tamanho": tamanho,
        }

    # Textos que não possuem nenhum caractere alfanumérico (ex.: apenas espaços,
    # pontuação, quebras de linha ou caracteres de controle/surrogates)
    if not any(c.isalnum() for c in texto):
        return {
            "categoria": "sem_palavras",
            "urgente": urgente,
            "tamanho": tamanho,
        }

    # Normalização de caixa e remoção de acentos para classificação temática
    texto_norm = texto.translate(_ACCENT_MAP).lower()
    palavras = set(re.findall(r"\b\w+\b", texto_norm))

    # 1. Prioridade: Reclamação
    if any(p in palavras for p in _PALAVRAS_RECLAMACAO) or any(exp in texto_norm for exp in _EXPRESSOES_RECLAMACAO):
        categoria = "reclamacao"
    # 2. Prioridade: Dúvida (inclui sinal de interrogação '?')
    elif "?" in texto or any(p in palavras for p in _PALAVRAS_DUVIDA) or any(exp in texto_norm for exp in _EXPRESSOES_DUVIDA):
        categoria = "duvida"
    # 3. Prioridade: Pedido
    elif any(p in palavras for p in _PALAVRAS_PEDIDO):
        categoria = "pedido"
    # 4. Prioridade: Elogio
    elif any(p in palavras for p in _PALAVRAS_ELOGIO):
        categoria = "elogio"
    # 5. Outro
    else:
        categoria = "outro"

    return {
        "categoria": categoria,
        "urgente": urgente,
        "tamanho": tamanho,
    }
