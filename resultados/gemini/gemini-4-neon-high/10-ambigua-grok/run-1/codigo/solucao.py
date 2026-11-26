from __future__ import annotations

import re
import unicodedata

_CATEGORIA_PADROES: tuple[tuple[str, tuple[re.Pattern[str], ...]], ...] = (
    (
        "reclamacao",
        (
            re.compile(
                r"\b("
                r"reclamacao|reclamar|problema|problemas|erro|erros|falha|falhas|"
                r"defeito|quebrado|quebrou|nao\s+funciona|parou\s+de\s+funcionar|"
                r"pessimo|pessima|horrivel|ruim|insatisfeito|insatisfeita|"
                r"atraso|atrasado|atrasada|cobranca\s+indevida|estorno|reembolso|cancelar"
                r")\b"
            ),
        ),
    ),
    (
        "duvida",
        (
            re.compile(r"\?"),
            re.compile(
                r"\b("
                r"duvida|duvidas|pergunta|perguntas|como\s+faco|como\s+funciona|"
                r"onde\s+encontro|qual\s+e|quais\s+sao|quando|porque|por\s+que|"
                r"saber\s+se|poderia\s+explicar|pode\s+explicar|nao\s+entendi"
                r")\b"
            ),
        ),
    ),
    (
        "pedido",
        (
            re.compile(
                r"\b("
                r"preciso|gostaria|quero|solicito|solicitacao|pedido|pedir|"
                r"por\s+favor|poderia|pode\s+me|ajuda|ajudar|suporte|"
                r"enviar|envie|atualizar|atualize|alterar|altere|liberar|libere"
                r")\b"
            ),
        ),
    ),
    (
        "elogio",
        (
            re.compile(
                r"\b("
                r"obrigado|obrigada|valeu|agradeco|agradecimento|"
                r"parabens|otimo|otima|excelente|perfeito|perfeita|"
                r"muito\s+bom|muito\s+boa|adorei|amei|gostei|"
                r"maravilhoso|maravilhosa|satisfeito|satisfeita|eficiente|rapido"
                r")\b"
            ),
        ),
    ),
)


def _normalizar_para_classificacao(texto: str) -> str:
    """Remove acentos (NFKD sem marcas combinantes) e aplica casefold."""
    decomposed = unicodedata.normalize("NFKD", texto)
    sem_acentos = "".join(
        ch for ch in decomposed if unicodedata.category(ch) != "Mn"
    )
    return sem_acentos.casefold()


def _detectar_categoria(texto: str) -> str:
    if texto == "":
        return "vazia"

    if not any(ch.isalnum() for ch in texto):
        return "sem_conteudo"

    normalizado = _normalizar_para_classificacao(texto)
    for categoria, padroes in _CATEGORIA_PADROES:
        if any(padrao.search(normalizado) for padrao in padroes):
            return categoria

    return "outro"


def classificar_mensagem(texto: str) -> dict:
    """Classifica uma mensagem curta de forma pura e determinística."""
    if not isinstance(texto, str):
        raise TypeError(
            f"texto deve ser str, recebido {type(texto).__name__}"
        )

    return {
        "categoria": _detectar_categoria(texto),
        "urgente": "URGENTE" in texto,
        "tamanho": len(texto),
    }
