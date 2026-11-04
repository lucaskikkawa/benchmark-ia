DIGITOS = frozenset("0123456789")
MINUTOS_DIA = 1440


def _para_minutos(horario: str) -> int:
    """Converte 'HH:MM' em minutos desde 00:00. Aceita '24:00' como 1440."""
    if not isinstance(horario, str):
        raise TypeError(f"horário deve ser str, não {type(horario).__name__}")
    if len(horario) != 5 or horario[2] != ":":
        raise ValueError(f"horário inválido: {horario!r}")
    hh_txt, mm_txt = horario[:2], horario[3:]
    if not all(c in DIGITOS for c in hh_txt + mm_txt):
        raise ValueError(f"horário inválido: {horario!r}")
    hh, mm = int(hh_txt), int(mm_txt)
    if mm > 59 or hh > 24 or (hh == 24 and mm != 0):
        raise ValueError(f"horário inválido: {horario!r}")
    return hh * 60 + mm


def _para_texto(minutos: int) -> str:
    """Converte minutos em 'HH:MM'. 1440 vira '24:00'."""
    if minutos == MINUTOS_DIA:
        return "24:00"
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    if not isinstance(ocupados, list):
        raise TypeError("ocupados deve ser list")

    janela_ini = _para_minutos(inicio)
    janela_fim = _para_minutos(fim)
    if janela_ini >= janela_fim:
        raise ValueError("inicio deve ser estritamente anterior a fim")

    # Valida tudo antes de descartar ou recortar qualquer item.
    recortados = []
    for item in ocupados:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise TypeError("cada ocupado deve ser par (ini, fim)")
        ini, fim_ocupado = _para_minutos(item[0]), _para_minutos(item[1])
        if ini > fim_ocupado:
            raise ValueError(f"intervalo com início após o fim: {item!r}")
        if ini == fim_ocupado:
            continue

        # Recorte para a janela; o que ficar vazio some.
        ini = max(ini, janela_ini)
        fim_ocupado = min(fim_ocupado, janela_fim)
        if ini < fim_ocupado:
            recortados.append((ini, fim_ocupado))

    # Une intervalos que se sobrepõem ou se encostam, após o recorte.
    recortados.sort()
    unidos = []
    for ini, fim_ocupado in recortados:
        if unidos and ini <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], fim_ocupado)
        else:
            unidos.append([ini, fim_ocupado])

    # Os trechos entre os ocupados unidos são as folgas.
    livres = []
    cursor = janela_ini
    for ini, fim_ocupado in unidos:
        if ini > cursor:
            livres.append((_para_texto(cursor), _para_texto(ini)))
        cursor = max(cursor, fim_ocupado)
    if cursor < janela_fim:
        livres.append((_para_texto(cursor), _para_texto(janela_fim)))

    return livres
