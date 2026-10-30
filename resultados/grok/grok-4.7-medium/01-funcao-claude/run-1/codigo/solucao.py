"""Converte durações humanas (w/d/h/m/s) em segundos."""

_MULTIPLICADORES = {
    "w": 604800,
    "d": 86400,
    "h": 3600,
    "m": 60,
    "s": 1,
}
_ORDEM = {"w": 0, "d": 1, "h": 2, "m": 3, "s": 4}
# int() recusa strings com mais de 4300 dígitos por padrão; blocos menores evitam o limite.
_BLOCO = 4000


def _inteiro(digitos: str) -> int:
    valor = 0
    for i in range(0, len(digitos), _BLOCO):
        bloco = digitos[i:i + _BLOCO]
        valor = valor * 10 ** len(bloco) + int(bloco)
    return valor


def parse_duracao(texto: str) -> int:
    """Converte uma duração em segundos.

    Aceita de 1 a 5 componentes ``<inteiro><unidade>`` na ordem w, d, h, m, s.
    Levanta TypeError se ``texto`` não for str e ValueError se o formato for inválido.
    """
    if not isinstance(texto, str):
        raise TypeError("texto deve ser str")

    # str.split ignora override de subclasses e colapsa qualquer whitespace.
    partes = str.split(texto)
    if not partes:
        raise ValueError("duração vazia")

    total = 0
    anterior = -1
    encontrou = False

    for parte in partes:
        i = 0
        n = len(parte)
        while i < n:
            if not ("0" <= parte[i] <= "9"):
                raise ValueError("formato inválido")
            j = i + 1
            while j < n and "0" <= parte[j] <= "9":
                j += 1
            if j == n:
                raise ValueError("número sem unidade")
            unidade = parte[j].lower()
            ordem = _ORDEM.get(unidade)
            if ordem is None or ordem <= anterior:
                raise ValueError("unidade inválida, repetida ou fora de ordem")
            anterior = ordem
            total += _inteiro(parte[i:j]) * _MULTIPLICADORES[unidade]
            encontrou = True
            i = j + 1

    if not encontrou:
        raise ValueError("formato inválido")
    return total
