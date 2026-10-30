_DIGITOS_ASCII = frozenset("0123456789")


def _parse_horario(horario: str) -> int:
    if not isinstance(horario, str):
        raise TypeError("Horário deve ser uma string")
    if len(horario) != 5 or horario[2] != ":":
        raise ValueError(f"Horário em formato inválido: {horario!r}")
    h1, h2, _, m1, m2 = horario
    if (
        h1 not in _DIGITOS_ASCII
        or h2 not in _DIGITOS_ASCII
        or m1 not in _DIGITOS_ASCII
        or m2 not in _DIGITOS_ASCII
    ):
        raise ValueError(f"Horário deve conter apenas dígitos ASCII: {horario!r}")
    if horario == "24:00":
        return 1440
    horas = (ord(h1) - 48) * 10 + (ord(h2) - 48)
    minutos = (ord(m1) - 48) * 10 + (ord(m2) - 48)
    if horas > 23 or minutos > 59:
        raise ValueError(f"Horário fora do intervalo permitido: {horario!r}")
    return horas * 60 + minutos


def _format_horario(total_minutos: int) -> str:
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

    janela_ini = _parse_horario(inicio)
    janela_fim = _parse_horario(fim)
    if janela_ini >= janela_fim:
        raise ValueError("inicio deve ser estritamente anterior a fim")

    intervalos_recortados: list[tuple[int, int]] = []
    for item in ocupados:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise TypeError(
                "Cada item de ocupados deve ser um tuple ou list de 2 elementos"
            )
        ini_str, fim_str = item
        if not isinstance(ini_str, str) or not isinstance(fim_str, str):
            raise TypeError("Os limites de cada intervalo devem ser strings")
        ini_min = _parse_horario(ini_str)
        fim_min = _parse_horario(fim_str)
        if ini_min > fim_min:
            raise ValueError("O início do intervalo não pode ser maior que o fim")
        if ini_min == fim_min:
            continue
        recorte_ini = max(ini_min, janela_ini)
        recorte_fim = min(fim_min, janela_fim)
        if recorte_ini < recorte_fim:
            intervalos_recortados.append((recorte_ini, recorte_fim))

    if not intervalos_recortados:
        return [(_format_horario(janela_ini), _format_horario(janela_fim))]

    intervalos_recortados.sort()
    fundidos: list[tuple[int, int]] = []
    atual_ini, atual_fim = intervalos_recortados[0]
    for prox_ini, prox_fim in intervalos_recortados[1:]:
        if prox_ini <= atual_fim:
            if prox_fim > atual_fim:
                atual_fim = prox_fim
        else:
            fundidos.append((atual_ini, atual_fim))
            atual_ini, atual_fim = prox_ini, prox_fim
    fundidos.append((atual_ini, atual_fim))

    livres: list[tuple[str, str]] = []
    cursor = janela_ini
    for ocu_ini, ocu_fim in fundidos:
        if cursor < ocu_ini:
            livres.append((_format_horario(cursor), _format_horario(ocu_ini)))
        cursor = ocu_fim
    if cursor < janela_fim:
        livres.append((_format_horario(cursor), _format_horario(janela_fim)))

    return livres
