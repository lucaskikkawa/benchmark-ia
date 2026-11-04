def _parse_horario(s: str) -> int:
    if type(s) is not str:
        raise TypeError(f"Horário deve ser str, recebido {type(s).__name__}")
    if len(s) != 5:
        raise ValueError(f"Horário deve ter exatamente 5 caracteres: {s!r}")
    if s[2] != ":":
        raise ValueError(f"Separador deve ser ':' (U+003A): {s!r}")
    digits = "0123456789"
    if s[0] not in digits or s[1] not in digits or s[3] not in digits or s[4] not in digits:
        raise ValueError(f"Dígitos devem ser ASCII de 0 a 9: {s!r}")
    if s == "24:00":
        return 1440
    h = int(s[:2])
    m = int(s[3:])
    if not (0 <= h <= 23 and 0 <= m <= 59):
        raise ValueError(f"Horário fora dos limites permitidos: {s!r}")
    return h * 60 + m


def _format_horario(m: int) -> str:
    if m == 1440:
        return "24:00"
    h = m // 60
    mins = m % 60
    return f"{h:02d}:{mins:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    if type(ocupados) is not list:
        raise TypeError(f"ocupados deve ser exatamente uma list, recebido {type(ocupados).__name__}")

    w_ini = _parse_horario(inicio)
    w_fim = _parse_horario(fim)
    if w_ini >= w_fim:
        raise ValueError(f"inicio ({inicio}) deve ser estritamente anterior a fim ({fim})")

    clipped_intervals: list[tuple[int, int]] = []
    for item in ocupados:
        if type(item) not in (tuple, list):
            raise TypeError(f"Cada item de ocupados deve ser tuple ou list, recebido {type(item).__name__}")
        if len(item) != 2:
            raise TypeError(f"Cada item de ocupados deve ter exatamente 2 elementos, recebido {len(item)}")

        ini_str, fim_str = item
        if type(ini_str) is not str or type(fim_str) is not str:
            raise TypeError("Horários em ocupados devem ser strings")

        o_ini = _parse_horario(ini_str)
        o_fim = _parse_horario(fim_str)

        if o_ini > o_fim:
            raise ValueError(f"Horário de início ({ini_str}) posterior ao de fim ({fim_str})")

        if o_ini == o_fim:
            continue

        c_ini = max(o_ini, w_ini)
        c_fim = min(o_fim, w_fim)
        if c_ini < c_fim:
            clipped_intervals.append((c_ini, c_fim))

    clipped_intervals.sort(key=lambda x: (x[0], x[1]))

    merged: list[list[int]] = []
    for cur_ini, cur_fim in clipped_intervals:
        if not merged:
            merged.append([cur_ini, cur_fim])
        else:
            prev = merged[-1]
            if cur_ini <= prev[1]:
                prev[1] = max(prev[1], cur_fim)
            else:
                merged.append([cur_ini, cur_fim])

    livres: list[tuple[str, str]] = []
    cursor = w_ini
    for m_ini, m_fim in merged:
        if cursor < m_ini:
            livres.append((_format_horario(cursor), _format_horario(m_ini)))
        cursor = max(cursor, m_fim)
    if cursor < w_fim:
        livres.append((_format_horario(cursor), _format_horario(w_fim)))

    return livres
