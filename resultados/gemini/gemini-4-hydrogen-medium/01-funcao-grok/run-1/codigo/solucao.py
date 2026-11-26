_DIGITS = frozenset("0123456789")
_MINUTES_PER_DAY = 24 * 60


def _parse_time(value: str) -> int:
    if not isinstance(value, str):
        raise TypeError(f"Horário deve ser str, recebido {type(value).__name__}")
    if (
        len(value) != 5
        or value[2] != ":"
        or value[0] not in _DIGITS
        or value[1] not in _DIGITS
        or value[3] not in _DIGITS
        or value[4] not in _DIGITS
    ):
        raise ValueError(f"Horário inválido: {value!r}")

    hours = int(value[:2])
    minutes = int(value[3:])

    if hours == 24:
        if minutes != 0:
            raise ValueError(f"Horário inválido: {value!r}")
        return _MINUTES_PER_DAY

    if hours > 23 or minutes > 59:
        raise ValueError(f"Horário inválido: {value!r}")

    return hours * 60 + minutes


def _format_time(total_minutes: int) -> str:
    if total_minutes == _MINUTES_PER_DAY:
        return "24:00"
    hours, minutes = divmod(total_minutes, 60)
    return f"{hours:02d}:{minutes:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    if not isinstance(ocupados, list):
        raise TypeError(
            f"ocupados deve ser list, recebido {type(ocupados).__name__}"
        )

    win_start = _parse_time(inicio)
    win_end = _parse_time(fim)
    if win_start >= win_end:
        raise ValueError("inicio deve ser estritamente anterior a fim")

    clipped: list[tuple[int, int]] = []
    for item in ocupados:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise TypeError(
                "Cada item de ocupados deve ser tuple ou list de exatamente 2 strings"
            )
        busy_start = _parse_time(item[0])
        busy_end = _parse_time(item[1])
        if busy_start > busy_end:
            raise ValueError("Início do intervalo ocupado não pode ser maior que o fim")
        if busy_start == busy_end:
            continue

        start = max(busy_start, win_start)
        end = min(busy_end, win_end)
        if start < end:
            clipped.append((start, end))

    if not clipped:
        return [(_format_time(win_start), _format_time(win_end))]

    clipped.sort()
    merged: list[tuple[int, int]] = [clipped[0]]
    for start, end in clipped[1:]:
        prev_start, prev_end = merged[-1]
        if start <= prev_end:
            if end > prev_end:
                merged[-1] = (prev_start, end)
        else:
            merged.append((start, end))

    free: list[tuple[str, str]] = []
    cursor = win_start
    for busy_start, busy_end in merged:
        if cursor < busy_start:
            free.append((_format_time(cursor), _format_time(busy_start)))
        cursor = busy_end
    if cursor < win_end:
        free.append((_format_time(cursor), _format_time(win_end)))

    return free
