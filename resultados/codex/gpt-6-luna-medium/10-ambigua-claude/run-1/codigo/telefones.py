"""Utilities for normalizing Brazilian telephone numbers."""

import re


_SEPARADORES = re.compile(r"[\s().-]+")
_CARACTERES_PERMITIDOS = re.compile(r"\+?[\d\s().-]+\Z")


def _validar_digitos(digitos: str) -> str:
    """Validate a number without country prefix and return E.164."""
    if len(digitos) not in (10, 11):
        raise ValueError("telefone deve ter DDD e 8 ou 9 dígitos")

    ddd = digitos[:2]
    numero = digitos[2:]
    if int(ddd) < 11 or ddd[1] == "0":
        raise ValueError("DDD inválido")

    if len(numero) == 8 and numero[0] not in "2345":
        raise ValueError("prefixo de telefone fixo inválido")
    if len(numero) == 9 and numero[0] != "9":
        raise ValueError("prefixo de celular inválido")
    return "+55" + digitos


def normalizar_telefone(texto: str) -> str:
    """Normalize one Brazilian phone number to E.164."""
    if not isinstance(texto, str) or not texto or not _CARACTERES_PERMITIDOS.fullmatch(texto):
        raise ValueError("formato de telefone inválido")

    # Parênteses, quando usados, devem formar um único par ao redor do DDD.
    if texto.count("(") != texto.count(")") or texto.count("(") > 1:
        raise ValueError("parênteses inválidos")
    if "(" in texto and not re.search(r"\(\s*\d{2}\s*\)", texto):
        raise ValueError("parênteses devem envolver o DDD")

    digitos = re.sub(r"\D", "", texto)
    # O sinal de mais só é permitido antes do código do país.
    if texto.lstrip().startswith("+"):
        if not digitos.startswith("55"):
            raise ValueError("código de país inválido")
        digitos = digitos[2:]
    elif digitos.startswith("55") and len(digitos) in (12, 13):
        digitos = digitos[2:]

    return _validar_digitos(digitos)


# Telefones em texto livre: parênteses opcionais no DDD, código do país opcional,
# e os separadores pedidos pelo enunciado. O lookaround impede recortes de uma
# sequência maior de algarismos.
_TELEFONE_RE = re.compile(
    r"(?<!\d)(?:\+?\s*55[\s.-]*)?"
    r"(?:\(\s*\d{2}\s*\)|\d{2})"
    r"(?:[\s.-]*\d){8,9}(?!\d)"
)


def extrair_telefones(texto: str) -> list[str]:
    """Find distinct valid Brazilian phones in free text, preserving order."""
    if not isinstance(texto, str):
        return []

    encontrados: list[str] = []
    vistos: set[str] = set()
    for match in _TELEFONE_RE.finditer(texto):
        try:
            telefone = normalizar_telefone(match.group())
        except ValueError:
            continue
        if telefone not in vistos:
            vistos.add(telefone)
            encontrados.append(telefone)
    return encontrados
