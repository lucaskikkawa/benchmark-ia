_DIGITOS = "0123456789"


def _para_minutos(h):
    if not isinstance(h, str):
        raise TypeError(f"horário deve ser str, recebido {type(h).__name__}")
    if (
        len(h) != 5
        or h[2] != ":"
        or any(c not in _DIGITOS for c in h[:2] + h[3:])
    ):
        raise ValueError(f"horário inválido: {h!r}")
    hh = int(h[:2])
    mm = int(h[3:])
    if mm > 59 or hh > 24 or (hh == 24 and mm != 0):
        raise ValueError(f"horário inválido: {h!r}")
    return hh * 60 + mm


def _formatar(m):
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

    if type(ocupados) is not list:
        raise TypeError("ocupados deve ser uma list")

    recortados = []
    for item in ocupados:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise TypeError(f"item de ocupados com forma inválida: {item!r}")
        a_txt, b_txt = item[0], item[1]
        if not isinstance(a_txt, str) or not isinstance(b_txt, str):
            raise TypeError(f"item de ocupados deve conter duas str: {item!r}")
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
    unidos = []
    for a, b in recortados:
        if unidos and a <= unidos[-1][1]:
            if b > unidos[-1][1]:
                unidos[-1][1] = b
        else:
            unidos.append([a, b])

    livres = []
    cursor = j_ini
    for a, b in unidos:
        if a > cursor:
            livres.append((_formatar(cursor), _formatar(a)))
        cursor = max(cursor, b)
    if cursor < j_fim:
        livres.append((_formatar(cursor), _formatar(j_fim)))
    return livres
