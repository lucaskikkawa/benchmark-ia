"""Módulo para cálculo de horários livres em uma janela de disponibilidade."""

ASCII_DIGITS = set("0123456789")


def _parse_horario(h: str) -> int:
    """Valida e converte um horário no formato 'HH:MM' para minutos desde 00:00.

    Levanta TypeError se não for str.
    Levanta ValueError se formato ou valores forem inválidos.
    """
    if not isinstance(h, str):
        raise TypeError(f"Horário deve ser str, recebido: {type(h).__name__}")
    if len(h) != 5:
        raise ValueError(f"Horário deve ter exatamente 5 caracteres: {h!r}")
    if h[2] != ":":
        raise ValueError(f"Separador deve ser ':', recebido: {h[2]!r}")
    if (
        h[0] not in ASCII_DIGITS
        or h[1] not in ASCII_DIGITS
        or h[3] not in ASCII_DIGITS
        or h[4] not in ASCII_DIGITS
    ):
        raise ValueError(f"Caracteres inválidos no horário: {h!r}")

    hh = int(h[0:2])
    mm = int(h[3:5])

    if hh == 24:
        if mm == 0:
            return 1440
        raise ValueError(f"Minutos devem ser 00 para hora 24: {h!r}")

    if 0 <= hh <= 23 and 0 <= mm <= 59:
        return hh * 60 + mm

    raise ValueError(f"Horário fora dos limites válidos: {h!r}")


def _format_horario(minutos: int) -> str:
    """Converte minutos desde 00:00 para string 'HH:MM' (1440 -> '24:00')."""
    if minutos == 1440:
        return "24:00"
    hh = minutos // 60
    mm = minutos % 60
    return f"{hh:02d}:{mm:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    if type(ocupados) is not list:
        raise TypeError(f"ocupados deve ser list, recebido: {type(ocupados).__name__}")

    if not isinstance(inicio, str) or not isinstance(fim, str):
        raise TypeError("inicio e fim devem ser str")

    w_ini = _parse_horario(inicio)
    w_fim = _parse_horario(fim)

    if w_ini >= w_fim:
        raise ValueError(f"inicio ({inicio}) deve ser estritamente anterior a fim ({fim})")

    clipped: list[tuple[int, int]] = []
    for item in ocupados:
        if not isinstance(item, (tuple, list)):
            raise TypeError(f"Item de ocupados deve ser tuple ou list, recebido: {type(item).__name__}")
        if len(item) != 2:
            raise TypeError(f"Item de ocupados deve ter exatamente 2 elementos, recebido: {len(item)}")

        s_ini, s_fim = item
        if not isinstance(s_ini, str) or not isinstance(s_fim, str):
            raise TypeError("Horários dentro do intervalo ocupado devem ser str")

        t_ini = _parse_horario(s_ini)
        t_fim = _parse_horario(s_fim)

        if t_ini > t_fim:
            raise ValueError(f"Início ({s_ini}) posterior ao fim ({s_fim}) no intervalo")

        if t_ini == t_fim:
            continue

        c_ini = max(t_ini, w_ini)
        c_fim = min(t_fim, w_fim)
        if c_ini < c_fim:
            clipped.append((c_ini, c_fim))

    if not clipped:
        return [(_format_horario(w_ini), _format_horario(w_fim))]

    clipped.sort()

    merged: list[tuple[int, int]] = []
    for c_ini, c_fim in clipped:
        if not merged:
            merged.append((c_ini, c_fim))
        else:
            last_ini, last_fim = merged[-1]
            if c_ini <= last_fim:
                merged[-1] = (last_ini, max(last_fim, c_fim))
            else:
                merged.append((c_ini, c_fim))

    livres: list[tuple[str, str]] = []
    curr = w_ini
    for m_ini, m_fim in merged:
        if curr < m_ini:
            livres.append((_format_horario(curr), _format_horario(m_ini)))
        curr = m_fim
    if curr < w_fim:
        livres.append((_format_horario(curr), _format_horario(w_fim)))

    return livres
