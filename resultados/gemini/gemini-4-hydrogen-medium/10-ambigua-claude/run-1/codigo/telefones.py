"""Normalização e extração de números de telefone brasileiros no padrão E.164."""

import re

_ALLOWED_CHARS_RE = re.compile(r"^[0-9+\-.()\s]+$")
_CPF_FORMAT_RE = re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$")

_SEP = r"[ \t\u00a0.-]*"
_COUNTRY = r"(?:\+[ \t\u00a0]*55|\([ \t\u00a0]*\+?55[ \t\u00a0]*\)|55)"
_DDD = r"(?:\([ \t\u00a0]*[1-9]{2}[ \t\u00a0]*\)|[1-9]{2})"
_MOBILE = r"9(?:[ \t\u00a0.-]*\d){8}"
_LANDLINE = r"[2-5](?:[ \t\u00a0.-]*\d){7}"

_PHONE_EXTRACT_RE = re.compile(
    rf"(?<![\d+])(?<!\d[-.])"
    rf"(?:{_COUNTRY}{_SEP})?"
    rf"{_DDD}{_SEP}"
    rf"(?:{_MOBILE}|{_LANDLINE})"
    rf"(?!\d)(?![-.]\d)"
)


def _validate_parens_and_plus(texto: str) -> bool:
    """Valida uso de parênteses (balanceados, sem aninhamento) e do sinal '+'."""
    in_parens = False
    digits_in_parens = 0
    seen_digit = False
    plus_count = 0

    for idx, ch in enumerate(texto):
        if ch == "(":
            if in_parens:
                return False
            in_parens = True
            digits_in_parens = 0
        elif ch == ")":
            if not in_parens or digits_in_parens == 0:
                return False
            in_parens = False
        elif ch == "+":
            plus_count += 1
            if plus_count > 1 or seen_digit:
                return False
            # '+' só é permitido no início ou logo após '(' inicial (ex.: "(+55)")
            prefix = texto[:idx].strip()
            if prefix not in ("", "("):
                return False
        elif ch.isdigit():
            seen_digit = True
            if in_parens:
                digits_in_parens += 1

    return not in_parens


def _validate_national_digits(digitos: str, has_plus: bool) -> str:
    """Valida dígitos nacionais/internacionais e retorna '+55' + DDD + número."""
    n = len(digitos)
    if has_plus:
        if n not in (12, 13) or not digitos.startswith("55"):
            raise ValueError("Número com '+' deve conter código do país 55 e 10 ou 11 dígitos nacionais.")
        nacional = digitos[2:]
    elif n in (12, 13):
        if not digitos.startswith("55"):
            raise ValueError("Número com 12 ou 13 dígitos deve começar com o código do país 55.")
        nacional = digitos[2:]
    elif n in (10, 11):
        nacional = digitos
    else:
        raise ValueError(f"Quantidade inválida de dígitos ({n}).")

    ddd = nacional[:2]
    numero = nacional[2:]

    if "0" in ddd:
        raise ValueError(f"DDD inválido: {ddd!r}.")

    if len(numero) == 8:
        if numero[0] not in "2345":
            raise ValueError(f"Número fixo inválido: {numero!r}.")
    elif len(numero) == 9:
        if numero[0] != "9":
            raise ValueError(f"Número celular inválido: {numero!r}.")
    else:
        raise ValueError(f"Tamanho inválido do número: {numero!r}.")

    return f"+55{ddd}{numero}"


def normalizar_telefone(texto: str) -> str:
    """Normaliza um único telefone brasileiro para o formato E.164 ('+55...').

    Levanta ValueError se o texto não puder ser interpretado como um telefone válido.
    """
    if not isinstance(texto, str):
        raise ValueError("O telefone deve ser uma string.")

    limpo = texto.strip()
    if not limpo:
        raise ValueError("Telefone vazio.")

    if not _ALLOWED_CHARS_RE.match(limpo):
        raise ValueError(f"Caracteres inválidos no telefone: {texto!r}.")

    if not _validate_parens_and_plus(limpo):
        raise ValueError(f"Formatação inválida de parênteses ou '+' no telefone: {texto!r}.")

    digitos = "".join(ch for ch in limpo if ch.isdigit())
    return _validate_national_digits(digitos, has_plus="+" in limpo)


def extrair_telefones(texto: str) -> list[str]:
    """Extrai e normaliza telefones brasileiros de um texto livre, sem repetições."""
    if not isinstance(texto, str):
        raise ValueError("O texto deve ser uma string.")

    resultados: list[str] = []
    vistos: set[str] = set()

    for match in _PHONE_EXTRACT_RE.finditer(texto):
        trecho = match.group(0)
        if _CPF_FORMAT_RE.fullmatch(trecho):
            continue
        try:
            normalizado = normalizar_telefone(trecho)
        except ValueError:
            continue
        if normalizado not in vistos:
            vistos.add(normalizado)
            resultados.append(normalizado)

    return resultados
