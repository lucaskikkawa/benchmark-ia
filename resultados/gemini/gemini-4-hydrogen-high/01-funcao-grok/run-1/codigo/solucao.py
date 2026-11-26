"""Cálculo de intervalos horários livres dentro de uma janela."""

_ASCII_DIGITS = frozenset("0123456789")
_MINUTOS_DIA = 24 * 60


def _parse_horario(valor: object) -> int:
    """Converte uma string HH:MM válida para minutos desde 00:00."""
    if not isinstance(valor, str):
        raise TypeError(f"Horário deve ser str, recebido {type(valor).__name__}.")
    if len(valor) != 5 or valor[2] != ":":
        raise ValueError(f"Horário inválido: {valor!r}.")
    if (
        valor[0] not in _ASCII_DIGITS
        or valor[1] not in _ASCII_DIGITS
        or valor[3] not in _ASCII_DIGITS
        or valor[4] not in _ASCII_DIGITS
    ):
        raise ValueError(f"Horário inválido: {valor!r}.")

    horas = int(valor[0:2])
    minutos = int(valor[3:5])
    if horas == 24:
        if minutos != 0:
            raise ValueError(f"Horário inválido: {valor!r}.")
        return _MINUTOS_DIA
    if horas > 23 or minutos > 59:
        raise ValueError(f"Horário inválido: {valor!r}.")
    return horas * 60 + minutos


def _format_horario(minutos: int) -> str:
    """Converte minutos desde 00:00 para string HH:MM."""
    if minutos == _MINUTOS_DIA:
        return "24:00"
    horas, mins = divmod(minutos, 60)
    return f"{horas:02d}:{mins:02d}"


def _parse_ocupado(item: object) -> tuple[int, int]:
    """Valida um par (ini, fim) de ocupado e retorna os limites em minutos."""
    if not isinstance(item, (tuple, list)) or len(item) != 2:
        raise TypeError("Cada ocupado deve ser tuple ou list de exatamente 2 strings.")
    ini_str, fim_str = item
    ini = _parse_horario(ini_str)
    fim = _parse_horario(fim_str)
    if ini > fim:
        raise ValueError(f"Início {ini_str!r} posterior ao fim {fim_str!r}.")
    return ini, fim


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    if not isinstance(ocupados, list):
        raise TypeError(f"ocupados deve ser list, recebido {type(ocupados).__name__}.")

    win_ini = _parse_horario(inicio)
    win_fim = _parse_horario(fim)
    if win_ini >= win_fim:
        raise ValueError("inicio deve ser estritamente anterior a fim.")

    recortados: list[tuple[int, int]] = []
    for item in ocupados:
        ini, fim_item = _parse_ocupado(item)
        if ini == fim_item:
            continue
        rec_ini = max(ini, win_ini)
        rec_fim = min(fim_item, win_fim)
        if rec_ini < rec_fim:
            recortados.append((rec_ini, rec_fim))

    recortados.sort()

    unidos: list[tuple[int, int]] = []
    for ini, fim_item in recortados:
        if unidos and ini <= unidos[-1][1]:
            if fim_item > unidos[-1][1]:
                unidos[-1] = (unidos[-1][0], fim_item)
        else:
            unidos.append((ini, fim_item))

    livres: list[tuple[str, str]] = []
    cursor = win_ini
    for ini, fim_item in unidos:
        if cursor < ini:
            livres.append((_format_horario(cursor), _format_horario(ini)))
        cursor = fim_item
    if cursor < win_fim:
        livres.append((_format_horario(cursor), _format_horario(win_fim)))

    return livres
