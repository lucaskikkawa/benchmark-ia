"""Validação e extração de telefones brasileiros, sem dependências externas."""

import re


_SEPARADORES = re.compile(r"[ \t\r\n().-]")
_BLOCO = re.compile(r"[0-9+(). \t-]+")
_CPF_FORMATADO = re.compile(r"[0-9]{3}\.[0-9]{3}\.[0-9]{3}-[0-9]{2}")


def normalizar_telefone(texto: str) -> str:
    """Retorna um telefone em E.164 ou levanta ValueError se for inválido."""
    if not isinstance(texto, str):
        raise ValueError("O telefone deve ser uma string.")

    compacto = _SEPARADORES.sub("", texto)
    if re.fullmatch(r"\+?[0-9]+", compacto) is None:
        raise ValueError("Caracteres inválidos no telefone.")

    if compacto.startswith("+"):
        if not compacto.startswith("+55"):
            raise ValueError("O código do país deve ser 55.")
        nacional = compacto[3:]
    elif len(compacto) in (12, 13) and compacto.startswith("55"):
        nacional = compacto[2:]
    else:
        nacional = compacto

    if re.fullmatch(r"[1-9]{2}(?:[2-5][0-9]{7}|9[0-9]{8})", nacional) is None:
        raise ValueError("DDD ou número de telefone inválido.")
    return "+55" + nacional


def extrair_telefones(texto: str) -> list[str]:
    """Extrai candidatos completos e válidos, preservando a ordem e sem duplicatas."""
    if not isinstance(texto, str):
        raise ValueError("O texto deve ser uma string.")

    encontrados: list[str] = []
    vistos: set[str] = set()
    for correspondencia in _BLOCO.finditer(texto):
        candidato = correspondencia.group()
        inicio, fim = correspondencia.span()
        # Não reconhecer números colados a letras, '_' ou dígitos Unicode.
        if inicio and (texto[inicio - 1].isalnum() or texto[inicio - 1] == "_"):
            if candidato[0] in "+0123456789":
                continue
        if fim < len(texto) and (texto[fim].isalnum() or texto[fim] == "_"):
            if candidato[-1] in "+0123456789":
                continue

        if _CPF_FORMATADO.fullmatch(candidato.strip(" \t().-")):
            continue
        try:
            telefone = normalizar_telefone(candidato)
        except ValueError:
            continue
        if telefone not in vistos:
            vistos.add(telefone)
            encontrados.append(telefone)
    return encontrados
