"""Normalização de telefones brasileiros para E.164 (+55DDDNUMERO).

Decisões sobre casos não especificados estão em SUPOSICOES.md.
"""

import re

CODIGO_PAIS = "55"
# Separadores aceitos dentro de um telefone (além dos dígitos e do '+' inicial).
_SEPARADORES = re.compile(r"[\s().\-]")
# Candidato a telefone em texto livre: começa com '+', '(' ou dígito e continua
# com dígitos/separadores; termina num dígito.
_CANDIDATO = re.compile(r"(?<![\w+])(?:\+|\()?\d[\d\s().\-]*\d(?!\w)")


def _ddd_valido(ddd: str) -> bool:
    # DDDs brasileiros vão de 11 a 99 e nenhum termina em 0.
    return ddd[0] != "0" and ddd[1] != "0"


def _numero_valido(numero: str) -> bool:
    if len(numero) == 9:
        return numero[0] == "9"
    # Fixos começam com 2 a 5.
    return len(numero) == 8 and numero[0] in "2345"


def normalizar_telefone(texto: str) -> str:
    """Converte um telefone brasileiro para "+55DDDNUMERO".

    Aceita código do país opcional (55 ou +55), separadores (espaço, '-', '.', '(', ')')
    e um prefixo de operadora/longa distância '0' antes do DDD (ex.: "0 11 ...").

    Raises:
        TypeError: se texto não for str.
        ValueError: se o texto não for um telefone brasileiro válido.
    """
    if not isinstance(texto, str):
        raise TypeError("texto deve ser str")

    bruto = texto.strip()
    tem_mais = bruto.startswith("+")
    digitos = _SEPARADORES.sub("", bruto[1:] if tem_mais else bruto)
    if not digitos.isascii() or not digitos.isdigit():
        raise ValueError(f"telefone inválido: {texto!r}")

    if tem_mais:
        if not digitos.startswith(CODIGO_PAIS):
            raise ValueError(f"apenas números do Brasil (+55) são aceitos: {texto!r}")
        digitos = digitos[len(CODIGO_PAIS):]
    elif len(digitos) in (12, 13) and digitos.startswith(CODIGO_PAIS):
        digitos = digitos[len(CODIGO_PAIS):]
    elif len(digitos) in (11, 12) and digitos.startswith("0"):
        digitos = digitos[1:]  # prefixo de longa distância "0" antes do DDD

    ddd, numero = digitos[:2], digitos[2:]
    if len(digitos) not in (10, 11) or not _ddd_valido(ddd) or not _numero_valido(numero):
        raise ValueError(f"telefone inválido: {texto!r}")
    return f"+{CODIGO_PAIS}{ddd}{numero}"


def extrair_telefones(texto: str) -> list[str]:
    """Encontra telefones em texto livre e os devolve normalizados, sem repetição, em ordem.

    Trechos numéricos que não formam um telefone válido (datas, CPFs, valores) são ignorados.
    """
    if not isinstance(texto, str):
        raise TypeError("texto deve ser str")
    encontrados: dict[str, None] = {}
    for candidato in _CANDIDATO.finditer(texto):
        try:
            encontrados.setdefault(normalizar_telefone(candidato.group()))
        except ValueError:
            continue
    return list(encontrados)
