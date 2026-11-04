_DIGITOS_ASCII = frozenset("0123456789")


def _parse_horario(horario: str) -> int:
    if not isinstance(horario, str):
        raise TypeError("Horário deve ser uma string.")
    if (
        len(horario) != 5
        or horario[2] != ":"
        or horario[0] not in _DIGITOS_ASCII
        or horario[1] not in _DIGITOS_ASCII
        or horario[3] not in _DIGITOS_ASCII
        or horario[4] not in _DIGITOS_ASCII
    ):
        raise ValueError(f"Horário inválido: {horario!r}")

    horas = int(horario[:2])
    minutos = int(horario[3:])

    if horas == 24 and minutos == 0:
        return 1440
    if 0 <= horas <= 23 and 0 <= minutos <= 59:
        return horas * 60 + minutos
    raise ValueError(f"Horário fora do intervalo permitido: {horario!r}")


def _formatar_horario(total_minutos: int) -> str:
    horas, minutos = divmod(total_minutos, 60)
    return f"{horas:02d}:{minutos:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    if not isinstance(ocupados, list):
        raise TypeError("ocupados deve ser uma list.")

    ini_janela = _parse_horario(inicio)
    fim_janela = _parse_horario(fim)
    if ini_janela >= fim_janela:
        raise ValueError("inicio deve ser estritamente anterior a fim.")

    recortados: list[tuple[int, int]] = []
    for item in ocupados:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise TypeError(
                "Cada item de ocupados deve ser uma tuple ou list de 2 strings."
            )
        ini_str, fim_str = item[0], item[1]
        ini_min = _parse_horario(ini_str)
        fim_min = _parse_horario(fim_str)
        if ini_min > fim_min:
            raise ValueError("Início do intervalo ocupado posterior ao fim.")
        if ini_min == fim_min:
            continue

        c_ini = max(ini_min, ini_janela)
        c_fim = min(fim_min, fim_janela)
        if c_ini < c_fim:
            recortados.append((c_ini, c_fim))

    recortados.sort()

    unidos: list[tuple[int, int]] = []
    for c_ini, c_fim in recortados:
        if not unidos or c_ini > unidos[-1][1]:
            unidos.append((c_ini, c_fim))
        else:
            unidos[-1] = (unidos[-1][0], max(unidos[-1][1], c_fim))

    livres: list[tuple[str, str]] = []
    cursor = ini_janela
    for o_ini, o_fim in unidos:
        if cursor < o_ini:
            livres.append((_formatar_horario(cursor), _formatar_horario(o_ini)))
        cursor = o_fim

    if cursor < fim_janela:
        livres.append((_formatar_horario(cursor), _formatar_horario(fim_janela)))

    return livres
