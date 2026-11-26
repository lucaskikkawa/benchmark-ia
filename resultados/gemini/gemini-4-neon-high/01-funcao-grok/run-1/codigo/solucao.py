def _parse_horario(valor: object) -> int:
    if not isinstance(valor, str):
        raise TypeError("horário deve ser uma string")
    if (
        len(valor) != 5
        or valor[2] != ":"
        or not (
            "0" <= valor[0] <= "9"
            and "0" <= valor[1] <= "9"
            and "0" <= valor[3] <= "9"
            and "0" <= valor[4] <= "9"
        )
    ):
        raise ValueError(f"horário inválido: {valor!r}")

    horas = int(valor[0:2])
    minutos = int(valor[3:5])
    if horas == 24 and minutos == 0:
        return 1440
    if horas > 23 or minutos > 59:
        raise ValueError(f"horário fora do intervalo: {valor!r}")
    return horas * 60 + minutos


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
        raise TypeError("ocupados deve ser uma list")
    if not isinstance(inicio, str) or not isinstance(fim, str):
        raise TypeError("inicio e fim devem ser strings")

    janela_inicio = _parse_horario(inicio)
    janela_fim = _parse_horario(fim)
    if janela_inicio >= janela_fim:
        raise ValueError("inicio deve ser estritamente anterior a fim")

    recortados: list[tuple[int, int]] = []
    for item in ocupados:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise TypeError("cada item de ocupados deve ser tuple ou list de dois horários")
        ini_str, fim_str = item
        if not isinstance(ini_str, str) or not isinstance(fim_str, str):
            raise TypeError("cada horário em ocupados deve ser uma string")

        ini_min = _parse_horario(ini_str)
        fim_min = _parse_horario(fim_str)
        if ini_min > fim_min:
            raise ValueError("início do intervalo ocupado não pode ser posterior ao fim")
        if ini_min == fim_min:
            continue

        rec_ini = max(ini_min, janela_inicio)
        rec_fim = min(fim_min, janela_fim)
        if rec_ini < rec_fim:
            recortados.append((rec_ini, rec_fim))

    recortados.sort()

    fundidos: list[tuple[int, int]] = []
    for rec_ini, rec_fim in recortados:
        if not fundidos or rec_ini > fundidos[-1][1]:
            fundidos.append((rec_ini, rec_fim))
        elif rec_fim > fundidos[-1][1]:
            fundidos[-1] = (fundidos[-1][0], rec_fim)

    livres: list[tuple[str, str]] = []
    cursor = janela_inicio
    for b_ini, b_fim in fundidos:
        if cursor < b_ini:
            livres.append((_formatar_horario(cursor), _formatar_horario(b_ini)))
        cursor = b_fim
    if cursor < janela_fim:
        livres.append((_formatar_horario(cursor), _formatar_horario(janela_fim)))

    return livres
