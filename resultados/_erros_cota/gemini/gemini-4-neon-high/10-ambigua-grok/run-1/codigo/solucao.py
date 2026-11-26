"""Classificação determinística de mensagens curtas usando apenas a biblioteca padrão."""

from __future__ import annotations

import re
import unicodedata

_PALAVRA_RE = re.compile(r"[^\W_]+", re.UNICODE)

# Palavras isoladas (após NFD sem marcas combinantes + casefold) por categoria.
_PALAVRAS_CATEGORIA: dict[str, frozenset[str]] = {
    "reclamacao": frozenset(
        {
            "reclamacao",
            "reclamar",
            "problema",
            "problemas",
            "erro",
            "erros",
            "bug",
            "bugs",
            "falha",
            "falhas",
            "defeito",
            "quebrado",
            "quebrada",
            "pessimo",
            "pessima",
            "horrivel",
            "ruim",
            "atraso",
            "atrasado",
            "atrasada",
            "cancelar",
            "cancelamento",
            "reembolso",
            "estorno",
            "insatisfeito",
            "insatisfeita",
        }
    ),
    "pedido": frozenset(
        {
            "preciso",
            "gostaria",
            "quero",
            "solicito",
            "solicitacao",
            "pedido",
            "ajuda",
            "ajudar",
            "suporte",
            "envie",
            "enviar",
            "atualize",
            "atualizar",
            "altere",
            "alterar",
            "verifique",
            "verificar",
            "libere",
            "liberar",
            "agendar",
            "agendamento",
        }
    ),
    "duvida": frozenset(
        {
            "duvida",
            "duvidas",
            "pergunta",
            "perguntas",
            "como",
            "onde",
            "quando",
            "qual",
            "quais",
            "quanto",
            "porque",
        }
    ),
    "elogio": frozenset(
        {
            "obrigado",
            "obrigada",
            "agradeco",
            "parabens",
            "excelente",
            "otimo",
            "otima",
            "perfeito",
            "perfeita",
            "adorei",
            "maravilhoso",
            "maravilhosa",
            "satisfeito",
            "satisfeita",
            "elogio",
            "valeu",
        }
    ),
}

# Expressões compostas (comparadas por sequência exata de tokens normalizados).
_FRASES_CATEGORIA: dict[str, tuple[str, ...]] = {
    "reclamacao": (
        "nao funciona",
        "nao funcionou",
        "fora do ar",
        "cobranca indevida",
    ),
    "pedido": (
        "por favor",
    ),
    "duvida": (
        "por que",
        "sera que",
        "pode explicar",
        "nao entendi",
        "saber se",
    ),
    "elogio": (
        "muito bom",
        "muito boa",
        "bom trabalho",
    ),
}

# Ordem de desempate quando mais de uma categoria obtém a mesma pontuação.
_PRIORIDADE_DESEMPATE: tuple[str, ...] = (
    "reclamacao",
    "pedido",
    "duvida",
    "elogio",
)


def _normalizar_para_classificacao(texto: str) -> str:
    """Normaliza o texto removendo acentos (marcas combinantes) e ignorando maiúsculas."""
    decomposto = unicodedata.normalize("NFD", texto)
    sem_acentos = "".join(
        ch for ch in decomposto if unicodedata.category(ch) != "Mn"
    )
    return sem_acentos.casefold()


def _escolher_categoria(texto: str) -> str:
    normalizado = _normalizar_para_classificacao(texto)
    tokens = _PALAVRA_RE.findall(normalizado)
    if not tokens:
        return "sem_conteudo"

    conjunto_tokens = set(tokens)
    texto_tokens = f" {' '.join(tokens)} "

    melhor_categoria = "outro"
    melhor_pontuacao = 0

    for categoria in _PRIORIDADE_DESEMPATE:
        pontuacao = len(conjunto_tokens & _PALAVRAS_CATEGORIA[categoria])
        for frase in _FRASES_CATEGORIA[categoria]:
            if f" {frase} " in texto_tokens:
                pontuacao += 1
        if categoria == "duvida" and "?" in texto:
            pontuacao += 1

        if pontuacao > melhor_pontuacao:
            melhor_pontuacao = pontuacao
            melhor_categoria = categoria

    return melhor_categoria


def classificar_mensagem(texto: str) -> dict:
    """Classifica uma mensagem curta de forma pura e determinística.

    Retorna um dicionário com as chaves:
    - ``categoria`` (str): categoria atribuída à mensagem.
    - ``urgente`` (bool): ``True`` se e somente se ``"URGENTE"`` ocorre exatamente em ``texto``.
    - ``tamanho`` (int): ``len(texto)`` em code points, sem strip nem normalização.
    """
    if not isinstance(texto, str):
        raise TypeError(
            f"texto deve ser str, mas recebeu {type(texto).__name__}"
        )

    tamanho = len(texto)
    urgente = "URGENTE" in texto

    if texto == "":
        return {
            "categoria": "vazia",
            "urgente": False,
            "tamanho": 0,
        }

    categoria = _escolher_categoria(texto)
    return {
        "categoria": categoria,
        "urgente": urgente,
        "tamanho": tamanho,
    }
