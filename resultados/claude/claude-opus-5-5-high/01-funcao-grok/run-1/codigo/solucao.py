_DIGITOS = frozenset("0123456789")


def _para_minutos(h: object) -> int:
    if not isinstance(h, str):
        raise TypeError(f"horário deve ser str, recebido {type(h).__name__}")
    if (
        len(h) != 5
        or h[2] != ":"
        or not all(c in _DIGITOS for c in (h[0], h[1], h[3], h[4]))
    ):
        raise ValueError(f"horário inválido: {h!r}")
    horas = (ord(h[0]) - 48) * 10 + (ord(h[1]) - 48)
    minutos = (ord(h[3]) - 48) * 10 + (ord(h[4]) - 48)
    if minutos > 59:
        raise ValueError(f"horário inválido: {h!r}")
    if horas > 23 and not (horas == 24 and minutos == 0):
        raise ValueError(f"horário inválido: {h!r}")
    return horas * 60 + minutos


def _para_texto(m: int) -> str:
    return f"{m // 60:02d}:{m % 60:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    j_ini = _para_minutos(inicio)
    j_fim = _para_minutos(fim)
    if j_ini >= j_fim:
        raise ValueError("inicio deve ser estritamente anterior a fim")

    if not isinstance(ocupados, list):
        raise TypeError("ocupados deve ser uma list")

    recortados: list[tuple[int, int]] = []
    for item in ocupados:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise TypeError(f"item inválido em ocupados: {item!r}")
        a_txt, b_txt = item[0], item[1]
        a = _para_minutos(a_txt)
        b = _para_minutos(b_txt)
        if a > b:
            raise ValueError(f"intervalo com início após o fim: {item!r}")
        if a == b:
            continue
        a = max(a, j_ini)
        b = min(b, j_fim)
        if a < b:
            recortados.append((a, b))

    recortados.sort()
    unidos: list[list[int]] = []
    for a, b in recortados:
        if unidos and a <= unidos[-1][1]:
            if b > unidos[-1][1]:
                unidos[-1][1] = b
        else:
            unidos.append([a, b])

    livres: list[tuple[str, str]] = []
    cursor = j_ini
    for a, b in unidos:
        if a > cursor:
            livres.append((_para_texto(cursor), _para_texto(a)))
        cursor = max(cursor, b)
    if cursor < j_fim:
        livres.append((_para_texto(cursor), _para_texto(j_fim)))
    return livres
