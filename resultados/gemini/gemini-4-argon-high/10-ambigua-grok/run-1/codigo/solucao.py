from __future__ import annotations

import re
import unicodedata

_PALAVRAS_RECLAMACAO: frozenset[str] = frozenset(
    {
        "erro",
        "erros",
        "problema",
        "problemas",
        "falha",
        "falhas",
        "bug",
        "bugs",
        "defeito",
        "defeitos",
        "reclamacao",
        "reclamar",
        "ruim",
        "pessimo",
        "pessima",
        "lento",
        "lenta",
        "travou",
        "travando",
        "quebrado",
        "quebrada",
        "indisponivel",
        "inoperante",
    }
)

_FRASES_RECLAMACAO: tuple[str, ...] = (
    "nao funciona",
    "parou de funcionar",
    "fora do ar",
)

_PALAVRAS_PEDIDO: frozenset[str] = frozenset(
    {
        "pedido",
        "solicito",
        "solicitacao",
        "preciso",
        "quero",
        "favor",
        "ajuda",
        "suporte",
        "enviar",
        "envie",
        "cancelar",
        "cancele",
        "alterar",
        "atualizar",
        "liberar",
        "desbloquear",
    }
)

_PALAVRAS_DUVIDA: frozenset[str] = frozenset(
    {
        "duvida",
        "duvidas",
        "como",
        "onde",
        "quando",
        "qual",
        "quais",
        "porque",
        "quem",
        "quanto",
    }
)

_FRASES_DUVIDA: tuple[str, ...] = (
    "por que",
    "pode informar",
    "sabe dizer",
)

_PALAVRAS_ELOGIO: frozenset[str] = frozenset(
    {
        "elogio",
        "obrigado",
        "obrigada",
        "parabens",
        "excelente",
        "otimo",
        "otima",
        "perfeito",
        "perfeita",
        "bom",
        "boa",
        "adorei",
        "gostei",
        "satisfeito",
        "satisfeita",
    }
)

_REGEX_TOKENS = re.compile(r"[a-z0-9]+")


def _normalizar_para_busca(texto: str) -> str:
    minusculo = texto.lower()
    if minusculo.isascii():
        return minusculo
    decomposto = unicodedata.normalize("NFD", minusculo)
    return "".join(
        ch for ch in decomposto if unicodedata.category(ch) != "Mn"
    )


def classificar_mensagem(texto: str) -> dict:
    """Classifica uma mensagem curta de forma determinística e pura."""
    if not isinstance(texto, str):
        raise TypeError("O argumento 'texto' deve ser do tipo str.")

    tamanho = len(texto)
    urgente = "URGENTE" in texto

    if texto == "":
        return {
            "categoria": "vazia",
            "urgente": False,
            "tamanho": 0,
        }

    if not any(ch.isalnum() for ch in texto):
        return {
            "categoria": "sem_conteudo",
            "urgente": urgente,
            "tamanho": tamanho,
        }

    normalizado = _normalizar_para_busca(texto)
    lista_tokens = _REGEX_TOKENS.findall(normalizado)
    tokens = set(lista_tokens)
    texto_tokens = " ".join(lista_tokens)

    if (
        tokens & _PALAVRAS_RECLAMACAO
        or any(frase in texto_tokens for frase in _FRASES_RECLAMACAO)
    ):
        categoria = "reclamacao"
    elif tokens & _PALAVRAS_PEDIDO:
        categoria = "pedido"
    elif (
        "?" in texto
        or tokens & _PALAVRAS_DUVIDA
        or any(frase in texto_tokens for frase in _FRASES_DUVIDA)
    ):
        categoria = "duvida"
    elif tokens & _PALAVRAS_ELOGIO:
        categoria = "elogio"
    else:
        categoria = "outro"

    return {
        "categoria": categoria,
        "urgente": urgente,
        "tamanho": tamanho,
    }
