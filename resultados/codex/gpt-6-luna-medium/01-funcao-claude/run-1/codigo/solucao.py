"""Parser for human-readable durations, returning an exact number of seconds."""


_UNIDADES = {
    "w": (0, 604800),
    "d": (1, 86400),
    "h": (2, 3600),
    "m": (3, 60),
    "s": (4, 1),
}


def parse_duracao(texto: str) -> int:
    """Parse 1–5 ordered duration components and return their total in seconds.

    Components use ASCII digits followed by one of ``w``, ``d``, ``h``, ``m``
    or ``s`` (case-insensitive). Whitespace is allowed around/between
    components, but never inside one.
    """
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma string")

    tamanho = len(texto)
    pos = 0

    # Skip leading whitespace without allocating a trimmed copy (which also
    # keeps large whitespace-heavy inputs cheap).
    while pos < tamanho and texto[pos].isspace():
        pos += 1

    if pos == tamanho:
        raise ValueError("duração vazia")

    total = 0
    ultima_unidade = -1
    componentes = 0

    while pos < tamanho:
        inicio_numero = pos
        valor = 0
        while pos < tamanho:
            caractere = texto[pos]
            if not ("0" <= caractere <= "9"):
                break
            valor = valor * 10 + (ord(caractere) - ord("0"))
            pos += 1

        if pos == inicio_numero:
            raise ValueError("esperado um número ASCII")
        if pos == tamanho:
            raise ValueError("número sem unidade")

        unidade = texto[pos].lower()
        dados = _UNIDADES.get(unidade)
        if dados is None:
            raise ValueError("unidade inválida")
        ordem, fator = dados
        if ordem <= ultima_unidade:
            raise ValueError("unidades fora de ordem ou repetidas")

        total += valor * fator
        ultima_unidade = ordem
        componentes += 1
        if componentes > 5:
            raise ValueError("componentes demais")
        pos += 1

        # Whitespace separates complete components. Any non-whitespace next
        # character starts the next number and is validated by the next pass.
        while pos < tamanho and texto[pos].isspace():
            pos += 1

    return total
