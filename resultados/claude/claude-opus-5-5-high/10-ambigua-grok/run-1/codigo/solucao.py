"""Classificação simples de mensagens curtas (só biblioteca padrão, função pura)."""

import re
import unicodedata

# Ordem de prioridade usada para desempate (primeira vence).
_PRIORIDADE = ("reclamacao", "pedido", "duvida", "elogio")

# Palavras-gatilho já sem acento e em minúsculas (a comparação é feita
# sobre o texto normalizado da mesma forma). Entradas com espaço são
# expressões de várias palavras.
_GATILHOS = {
    "reclamacao": {
        "reclamacao", "reclamar", "reclamo", "problema", "problemas",
        "defeito", "quebrado", "quebrou", "pessimo", "pessima", "ruim",
        "horrivel", "absurdo", "atraso", "atrasado", "atrasou", "erro",
        "insatisfeito", "insatisfeita", "decepcionado", "decepcionada",
        "nao funciona", "nao chegou", "falha", "lixo", "cancelar",
    },
    "pedido": {
        "quero", "queria", "gostaria", "preciso", "solicito", "solicitar",
        "solicitacao", "pedido", "pedir", "envie", "enviem", "mande",
        "mandem", "favor", "por favor", "pfv", "pf", "poderia", "podem",
    },
    "duvida": {
        "como", "quando", "onde", "qual", "quais", "quanto", "quanta",
        "quantos", "quantas", "porque", "por que", "duvida", "duvidas",
        "sera", "alguem sabe",
    },
    "elogio": {
        "obrigado", "obrigada", "obg", "valeu", "parabens", "otimo",
        "otima", "excelente", "maravilhoso", "maravilhosa", "adorei",
        "amei", "gostei", "perfeito", "perfeita", "incrivel", "top",
        "show", "elogio", "bom", "boa",
    },
}

_PALAVRA = re.compile(r"[^\W_]+")


def _normalizar(texto):
    """Minúsculas (casefold) e remoção de acentos, só para a classificação."""
    decomposto = unicodedata.normalize("NFD", texto.casefold())
    return "".join(c for c in decomposto if not unicodedata.combining(c))


def classificar_mensagem(texto: str) -> dict:
    if not isinstance(texto, str):
        raise TypeError(
            "texto deve ser str, recebido %s" % type(texto).__name__
        )

    # Usa os métodos de str diretamente para não depender de overrides
    # em eventuais subclasses de str.
    tamanho = str.__len__(texto)
    urgente = str.__contains__(texto, "URGENTE")

    if tamanho == 0:
        return {
            "categoria": "vazia",
            "urgente": False,
            "tamanho": 0,
            "categorias_casadas": [],
        }

    normalizado = _normalizar(str.__str__(texto))
    palavras = _PALAVRA.findall(normalizado)

    if not palavras:
        return {
            "categoria": "sem_palavras",
            "urgente": urgente,
            "tamanho": tamanho,
            "categorias_casadas": [],
        }

    unigramas = set(palavras)
    bigramas = {" ".join(par) for par in zip(palavras, palavras[1:])}
    termos = unigramas | bigramas

    pontos = {}
    for categoria in _PRIORIDADE:
        n = len(_GATILHOS[categoria] & termos)
        if categoria == "duvida" and "?" in normalizado:
            n += 1
        if n:
            pontos[categoria] = n

    if pontos:
        maior = max(pontos.values())
        categoria = next(c for c in _PRIORIDADE if pontos.get(c) == maior)
    else:
        categoria = "outro"

    return {
        "categoria": categoria,
        "urgente": urgente,
        "tamanho": tamanho,
        "categorias_casadas": [c for c in _PRIORIDADE if c in pontos],
    }
