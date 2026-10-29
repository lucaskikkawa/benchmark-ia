"""Folgas dentro de uma janela de horários no mesmo dia."""


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Devolve os trechos livres de [inicio, fim).

    Horários são HH:MM. 24:00 marca o fim do dia. Intervalos ocupados de
    duração zero são ignorados. Sobrepostos ou encostados são unidos.
    Levanta TypeError para tipos errados e ValueError para horário, janela
    ou intervalo inválido.
    """
    if not isinstance(inicio, str) or not isinstance(fim, str):
        raise TypeError("horario deve ser str")
    if isinstance(ocupados, (str, bytes)) or not isinstance(ocupados, list):
        raise TypeError("ocupados deve ser uma lista")

    ini = _minutos(inicio)
    fim_min = _minutos(fim)
    if ini >= fim_min:
        raise ValueError("janela invalida")

    blocos: list[tuple[int, int]] = []
    for item in ocupados:
        if (
            isinstance(item, (str, bytes))
            or not isinstance(item, (tuple, list))
            or len(item) != 2
        ):
            raise TypeError("intervalo invalido")
        bruto_a, bruto_b = item
        if not isinstance(bruto_a, str) or not isinstance(bruto_b, str):
            raise TypeError("horario deve ser str")
        a = _minutos(bruto_a)
        b = _minutos(bruto_b)
        if a > b:
            raise ValueError("intervalo invalido")
        if a == b:
            continue
        a = max(a, ini)
        b = min(b, fim_min)
        if a < b:
            blocos.append((a, b))

    blocos.sort()
    fundidos: list[list[int]] = []
    for a, b in blocos:
        if not fundidos or a > fundidos[-1][1]:
            fundidos.append([a, b])
        else:
            fundidos[-1][1] = max(fundidos[-1][1], b)

    livres: list[tuple[str, str]] = []
    cursor = ini
    for a, b in fundidos:
        if cursor < a:
            livres.append((_formatar(cursor), _formatar(a)))
        cursor = max(cursor, b)
    if cursor < fim_min:
        livres.append((_formatar(cursor), _formatar(fim_min)))
    return livres


def _minutos(texto: str) -> int:
    if (
        len(texto) != 5
        or texto[2] != ":"
        or not texto[:2].isdigit()
        or not texto[3:].isdigit()
    ):
        raise ValueError(f"horario invalido: {texto}")
    hora = int(texto[:2])
    minuto = int(texto[3:])
    if hora == 24 and minuto == 0:
        return 24 * 60
    if hora > 23 or minuto > 59:
        raise ValueError(f"horario invalido: {texto}")
    return hora * 60 + minuto


def _formatar(total: int) -> str:
    hora, minuto = divmod(total, 60)
    return f"{hora:02d}:{minuto:02d}"
