"""Conversão de durações textuais para segundos."""

# Semanas, dias, horas, minutos, segundos — ordem obrigatória.
_UNIDADES = {
    "w": (0, 604800),
    "d": (1, 86400),
    "h": (2, 3600),
    "m": (3, 60),
    "s": (4, 1),
}


def parse_duracao(texto: str) -> int:
    """Converte uma duração humana no total em segundos.

    Aceita de 1 a 5 componentes ``<inteiro><unidade>`` (``w``, ``d``, ``h``,
    ``m``, ``s``), colados ou separados por espaços em branco, nessa ordem.
    """
    if not isinstance(texto, str):
        raise TypeError("texto deve ser str")

    # str.split descarta espaços em branco Unicode nas pontas e entre
    # componentes em tempo linear, sem copiar os trechos só de espaço.
    partes = str.split(texto)
    if not partes:
        raise ValueError("formato de duração inválido")

    total = 0
    ultima_ordem = -1

    for parte in partes:
        i = 0
        n = len(parte)
        while i < n:
            if not ("0" <= parte[i] <= "9"):
                raise ValueError("formato de duração inválido")
            j = i + 1
            while j < n and "0" <= parte[j] <= "9":
                j += 1
            if j >= n:
                raise ValueError("formato de duração inválido")
            info = _UNIDADES.get(parte[j].lower())
            if info is None:
                raise ValueError("formato de duração inválido")
            ordem, fator = info
            if ordem <= ultima_ordem:
                raise ValueError("formato de duração inválido")
            ultima_ordem = ordem
            total += int(parte[i:j]) * fator
            i = j + 1

    return total
