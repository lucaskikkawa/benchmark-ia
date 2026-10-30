"""Normalização e extração de telefones brasileiros."""

import re


_SEPARADORES_RE = re.compile(r"[ .()\t\n\r\v\f-]")


def _validar_digitos(digitos: str) -> str:
    """Valida DDD e número, aceitando prefixo nacional opcional 55."""
    if digitos.startswith("55") and len(digitos) in (12, 13):
        digitos = digitos[2:]

    if len(digitos) not in (10, 11):
        raise ValueError("telefone deve ter DDD e número com tamanho válido")

    ddd, numero = digitos[:2], digitos[2:]
    # DDDs vão de 11 a 99, exceto os terminados em zero.
    if ddd[0] == "0" or ddd[1] == "0":
        raise ValueError("DDD inválido")

    if len(numero) == 8 and numero[0] in "2345":
        return "+55" + digitos
    if len(numero) == 9 and numero[0] == "9":
        return "+55" + digitos
    raise ValueError("número fixo ou celular inválido")


def normalizar_telefone(texto: str) -> str:
    """Converte um telefone brasileiro para o formato E.164."""
    if not isinstance(texto, str):
        raise ValueError("telefone deve ser texto")

    valor = texto.strip()
    if not valor:
        raise ValueError("telefone vazio")

    com_mais = valor.startswith("+")
    if com_mais:
        valor = valor[1:]
    if "+" in valor:
        raise ValueError("sinal de + só pode aparecer no início")

    # O restante deve conter apenas dígitos ASCII e separadores de formatação.
    digitos = _SEPARADORES_RE.sub("", valor)
    if not digitos or re.fullmatch(r"[0-9]+", digitos) is None:
        raise ValueError("texto não pode ser interpretado como telefone")
    if com_mais and not digitos.startswith("55"):
        raise ValueError("+ deve ser seguido pelo código do Brasil 55")

    return _validar_digitos(digitos)


def extrair_telefones(texto: str) -> list[str]:
    """Extrai telefones válidos de texto livre, preservando a ordem."""
    if not isinstance(texto, str) or not texto:
        return []

    encontrados: list[tuple[int, str]] = []
    tamanho = len(texto)

    # Cada candidato começa no início de um trecho numérico (ou em +55).
    # Dentro dele só podem aparecer dígitos e separadores reconhecidos pelo
    # normalizador. Pontuação como vírgula e barra encerra o candidato.
    for inicio, caractere in enumerate(texto):
        if caractere not in "+0123456789":
            continue
        if inicio > 0 and texto[inicio - 1].isdigit():
            continue
        if inicio > 0 and texto[inicio - 1] == "+":
            continue
        if caractere == "+" and (inicio + 1 == tamanho or texto[inicio + 1] not in "0123456789"):
            continue

        fim = inicio + (1 if caractere == "+" else 0)
        while fim < tamanho and (texto[fim] in "0123456789" or _SEPARADORES_RE.fullmatch(texto[fim])):
            fim += 1
        if fim < tamanho and texto[fim] == "+":
            # Um + interno não pertence a um telefone válido.
            continue

        # Avalia cada prefixo terminado em dígito. Isso permite que um
        # telefone venha antes de outro número separado apenas por espaços.
        for final in range(inicio + 1, fim + 1):
            if texto[final - 1] not in "0123456789":
                continue
            if final < tamanho and texto[final].isdigit():
                continue
            candidato = texto[inicio:final]
            try:
                telefone = normalizar_telefone(candidato)
            except ValueError:
                continue
            encontrados.append((inicio, telefone))

    resultado: list[str] = []
    vistos: set[str] = set()
    for _, telefone in sorted(encontrados, key=lambda item: item[0]):
        if telefone not in vistos:
            vistos.add(telefone)
            resultado.append(telefone)
    return resultado
