"""Classificação simples e determinística de mensagens curtas.

Ver SUPOSICOES.md para as decisões tomadas nos pontos em aberto.
"""

import re
import unicodedata

# Ordem = prioridade de desempate quando o texto casa com mais de uma categoria.
_CATEGORIAS = (
    ("reclamacao", (
        "reclamacao", "reclamar", "reclamo", "problema", "problemas", "defeito",
        "quebrado", "quebrou", "pessimo", "pessima", "horrivel", "ruim",
        "insatisfeito", "insatisfeita", "absurdo", "nao funciona", "parou de funcionar",
        "atraso", "atrasado", "atrasada", "erro", "cobranca indevida", "decepcionado",
        "decepcionada", "reembolso",
    )),
    ("pedido", (
        "quero", "queria", "gostaria", "preciso", "solicito", "solicitar",
        "solicitacao", "pedido", "por favor", "favor", "envie", "enviar",
        "mande", "cancelar", "cancele", "trocar", "agendar", "contratar",
    )),
    ("duvida", (
        "duvida", "como", "quando", "onde", "qual", "quais", "quanto", "quanta",
        "quantos", "quantas", "por que", "porque", "pode me explicar", "sera que",
        "alguem sabe",
    )),
    ("elogio", (
        "obrigado", "obrigada", "parabens", "otimo", "otima", "excelente",
        "adorei", "amei", "gostei", "maravilhoso", "maravilhosa", "perfeito",
        "perfeita", "incrivel", "bom atendimento", "muito bom", "muito boa",
    )),
)

_PALAVRA = re.compile(r"\w+")
_PADROES = tuple(
    (nome, tuple(re.compile(r"(?<!\w)" + re.escape(t) + r"(?!\w)") for t in termos))
    for nome, termos in _CATEGORIAS
)


def _normalizar(texto):
    """Minúsculas, sem acentos, espaços colapsados. Nunca levanta erro."""
    decomposto = unicodedata.normalize("NFKD", texto.casefold())
    sem_acento = "".join(c for c in decomposto if not unicodedata.combining(c))
    return " ".join(sem_acento.split())


def classificar_mensagem(texto: str) -> dict:
    if not isinstance(texto, str):
        raise TypeError(
            "texto deve ser str, recebido %s" % type(texto).__name__
        )

    tamanho = len(texto)
    urgente = "URGENTE" in texto

    if texto == "":
        return {
            "categoria": "vazia",
            "urgente": False,
            "tamanho": 0,
            "categorias_casadas": [],
        }

    normal = _normalizar(texto)

    if not _PALAVRA.search(normal):
        categoria = "sem_conteudo"
        casadas = []
    else:
        casadas = [
            nome for nome, padroes in _PADROES
            if any(p.search(normal) for p in padroes)
        ]
        if not casadas and "?" in normal:
            casadas = ["duvida"]
        categoria = casadas[0] if casadas else "outro"

    return {
        "categoria": categoria,
        "urgente": urgente,
        "tamanho": tamanho,
        "categorias_casadas": casadas,
    }
