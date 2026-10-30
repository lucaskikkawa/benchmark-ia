"""Normalização e extração de telefones brasileiros, sem dependências externas."""

import re


_NUMERO_NACIONAL = re.compile(r"[1-9]{2}(?:[2-5][0-9]{7}|9[0-9]{8})")
# Inclui dígitos Unicode no candidato para que um dígito não ASCII não permita
# extrair, por acidente, um telefone de dentro de uma sequência maior.
_CANDIDATO = re.compile(r"[+\d](?:[+\d().\-\s]*[+\d])?")


def normalizar_telefone(texto: str) -> str:
    """Converte um telefone válido para +55DDDNÚMERO ou levanta ValueError.

    Aceita dígitos ASCII, um eventual '+' inicial e os separadores descritos
    em SUPOSICOES.md. Não acrescenta nem remove dígitos do número nacional.
    """
    if not isinstance(texto, str):
        raise ValueError("O telefone deve ser informado como texto.")

    compacto = "".join(
        caractere
        for caractere in texto
        if not (caractere.isspace() or caractere in "-().")
    )
    if re.fullmatch(r"\+?[0-9]+", compacto) is None:
        raise ValueError("O telefone contém caracteres inválidos ou está vazio.")

    tem_mais = compacto.startswith("+")
    digitos = compacto[1:] if tem_mais else compacto

    if len(digitos) in (12, 13) and digitos.startswith("55"):
        nacional = digitos[2:]
    elif not tem_mais and len(digitos) in (10, 11):
        nacional = digitos
    else:
        raise ValueError("Código de país ou quantidade de dígitos inválidos.")

    if _NUMERO_NACIONAL.fullmatch(nacional) is None:
        raise ValueError("DDD ou número de telefone inválido.")

    return "+55" + nacional


def extrair_telefones(texto: str) -> list[str]:
    """Extrai candidatos inteiros válidos, sem repetições e na ordem original.

    Quebras de linha delimitam candidatos. Dentro de cada linha, dígitos,
    '+', espaços, pontos, hífens e parênteses pertencem ao mesmo candidato.
    Sequências diretamente coladas a letras ou '_' são ignoradas.
    """
    if not isinstance(texto, str):
        raise ValueError("O conteúdo deve ser informado como texto.")

    encontrados: list[str] = []
    vistos: set[str] = set()
    for linha in texto.splitlines():
        for candidato in _CANDIDATO.finditer(linha):
            inicio, fim = candidato.span()
            anterior = linha[inicio - 1] if inicio else ""
            seguinte = linha[fim] if fim < len(linha) else ""
            if (
                anterior.isalnum()
                or anterior == "_"
                or seguinte.isalnum()
                or seguinte == "_"
            ):
                continue
            try:
                telefone = normalizar_telefone(candidato.group())
            except ValueError:
                continue
            if telefone not in vistos:
                vistos.add(telefone)
                encontrados.append(telefone)

    return encontrados
