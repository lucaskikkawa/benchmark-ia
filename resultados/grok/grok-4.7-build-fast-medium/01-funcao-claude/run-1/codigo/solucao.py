"""Converte durações humanas (ex.: ``1h30m``) em segundos."""

_MULT = {
    "w": 604800,
    "d": 86400,
    "h": 3600,
    "m": 60,
    "s": 1,
}
_RANK = {"w": 0, "d": 1, "h": 2, "m": 3, "s": 4}
_DIGIT = "0123456789"
# Abaixo do limite padrão de sys.int_info.default_max_str_digits (4300).
_CHUNK = 4000
_POW10_CHUNK = 10 ** _CHUNK


def _to_int(texto: str, i: int, j: int) -> int:
    """Inteiro exato de texto[i:j], sem o teto de dígitos de int(str)."""
    value = 0
    while i < j:
        k = i + _CHUNK
        if k >= j:
            value = value * (10 ** (j - i)) + int(texto[i:j])
            break
        value = value * _POW10_CHUNK + int(texto[i:k])
        i = k
    return value


def parse_duracao(texto: str) -> int:
    """Soma os componentes ``<inteiro><unidade>`` e devolve o total em segundos.

    Unidades, em ordem obrigatória e sem repetição: ``w`` ``d`` ``h`` ``m`` ``s``.
    Espaços em branco só separam componentes (nunca o número da unidade).
    """
    if not isinstance(texto, str):
        raise TypeError("texto deve ser str")

    n = len(texto)
    i = 0
    while i < n and texto[i].isspace():
        i += 1
    if i == n:
        raise ValueError("duração vazia")

    total = 0
    last = -1

    while i < n:
        if texto[i] not in _DIGIT:
            raise ValueError("formato inválido")

        j = i + 1
        while j < n and texto[j] in _DIGIT:
            j += 1
        if j == n:
            raise ValueError("número sem unidade")

        unit = texto[j]
        if "A" <= unit <= "Z":
            unit = chr(ord(unit) + 32)
        mult = _MULT.get(unit)
        if mult is None:
            raise ValueError("unidade inválida")

        rank = _RANK[unit]
        if rank <= last:
            raise ValueError("ordem inválida ou unidade repetida")
        last = rank

        total += _to_int(texto, i, j) * mult
        i = j + 1

        while i < n and texto[i].isspace():
            i += 1

    return total
