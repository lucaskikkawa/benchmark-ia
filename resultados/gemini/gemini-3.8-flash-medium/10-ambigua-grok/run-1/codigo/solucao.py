import re
import unicodedata

# Palavras-chave por categoria (normalizadas: sem acento e em minúsculas)
_TERMOS_RECLAMACAO = {
    "problema", "problemas", "defeito", "defeitos", "ruim", "pessimo",
    "pessima", "erro", "erros", "falha", "falhas", "cancelar",
    "cancelamento", "insatisfeito", "insatisfeita", "demora", "reclamacao",
    "reclamacoes", "pior", "prejuizo", "estorno", "nao funciona"
}

_TERMOS_DUVIDA = {
    "como", "quando", "onde", "por que", "porque", "qual", "quais",
    "quem", "quanto", "quantos", "duvida", "duvidas", "ajuda", "informacao",
    "informacoes", "saber", "funciona"
}

_TERMOS_PEDIDO = {
    "comprar", "compra", "pedido", "pedidos", "encomenda", "encomendas",
    "solicito", "solicitacao", "quero", "preco", "precos", "orcamento",
    "orcamentos", "cotacao", "cotacoes", "adquirir", "compro"
}

_TERMOS_ELOGIO = {
    "parabens", "otimo", "otima", "excelente", "excelentes", "bom",
    "boa", "bons", "boas", "adorei", "gostei", "maravilhoso", "maravilhosa",
    "perfeito", "perfeita", "obrigado", "obrigada", "valeu", "top"
}


def _remover_acentos_seguro(texto: str) -> str:
    """
    Remove acentos preservando surrogate code points que poderiam falhar
    ao passar diretamente para unicodedata.normalize().
    """
    chars = []
    for ch in texto:
        # Se for surrogate (\ud800 a \udfff), mantém inalterado
        if 0xD800 <= ord(ch) <= 0xDFFF:
            chars.append(ch)
        else:
            nfd = unicodedata.normalize("NFD", ch)
            chars.extend(c for c in nfd if unicodedata.category(c) != "Mn")
    return "".join(chars)


def classificar_mensagem(texto: str) -> dict:
    """
    Classifica uma mensagem de texto.

    Parâmetros:
        texto (str): O texto a ser classificado.

    Retorna:
        dict: Dicionário contendo:
            - 'categoria' (str): categoria da mensagem.
            - 'urgente' (bool): se contém a substring 'URGENTE'.
            - 'tamanho' (int): número de code points em texto.

    Lança:
        TypeError: se texto não for do tipo str.
    """
    if not isinstance(texto, str):
        raise TypeError(f"Esperado str, recebido {type(texto).__name__}")

    tamanho = len(texto)
    urgente = "URGENTE" in texto

    if texto == "":
        return {
            "categoria": "vazia",
            "urgente": False,
            "tamanho": 0,
        }

    # Pré-processamento para detecção de categoria (minúsculas e sem acento)
    texto_norm = _remover_acentos_seguro(texto).lower()

    # Extrai tokens de palavras
    palavras = set(re.findall(r"\w+", texto_norm))

    # Verifica presença de frases de duas palavras ("por que", "nao funciona")
    tem_reclamacao = bool(
        palavras.intersection(_TERMOS_RECLAMACAO)
        or "nao funciona" in texto_norm
    )
    tem_duvida = bool(
        "?" in texto
        or palavras.intersection(_TERMOS_DUVIDA)
        or "por que" in texto_norm
    )
    tem_pedido = bool(palavras.intersection(_TERMOS_PEDIDO))
    tem_elogio = bool(palavras.intersection(_TERMOS_ELOGIO))

    # Ordem de prioridade em caso de correspondência múltipla:
    # 1. Reclamação
    # 2. Dúvida
    # 3. Pedido
    # 4. Elogio
    # 5. Outro (padrão para textos não vazios sem correspondência)
    if tem_reclamacao:
        categoria = "reclamacao"
    elif tem_duvida:
        categoria = "duvida"
    elif tem_pedido:
        categoria = "pedido"
    elif tem_elogio:
        categoria = "elogio"
    else:
        categoria = "outro"

    return {
        "categoria": categoria,
        "urgente": urgente,
        "tamanho": tamanho,
    }
