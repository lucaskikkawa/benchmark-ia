import re


_COMPONENTES = re.compile(r"\s*[0-9]+[dDhHmMsS](?:\s*[0-9]+[dDhHmMsS]){0,3}\s*")
_UNIDADES = {"d": 86_400, "h": 3_600, "m": 60, "s": 1}
_ORDEM = {"d": 0, "h": 1, "m": 2, "s": 3}


def parse_duracao(texto: str) -> int:
    """Converte uma duração textual para o total de segundos."""
    if not isinstance(texto, str):
        raise TypeError("texto deve ser uma string")

    if not _COMPONENTES.fullmatch(texto):
        raise ValueError("formato de duração inválido")

    total = 0
    ultima_ordem = -1
    for numero, unidade in re.findall(r"([0-9]+)([dDhHmMsS])", texto):
        unidade = unidade.lower()
        ordem = _ORDEM[unidade]
        if ordem <= ultima_ordem:
            raise ValueError("unidades devem aparecer uma única vez e na ordem d, h, m, s")
        ultima_ordem = ordem
        total += int(numero) * _UNIDADES[unidade]

    return total
