def _minutos(horario: str) -> int:
    """Valida um horário HH:MM e o converte para minutos desde meia-noite."""
    if not isinstance(horario, str):
        raise TypeError("horário deve ser str")

    if len(horario) != 5 or horario[2] != ":":
        raise ValueError("horário deve estar no formato HH:MM")

    horas_txt = horario[:2]
    minutos_txt = horario[3:]
    if any(caractere not in "0123456789" for caractere in horas_txt + minutos_txt):
        raise ValueError("horário deve conter dígitos ASCII")

    horas = int(horas_txt)
    minutos = int(minutos_txt)
    if minutos > 59 or horas > 24 or (horas == 24 and minutos != 0):
        raise ValueError("horário fora do intervalo válido")

    return horas * 60 + minutos


def _formatar(minutos: int) -> str:
    if minutos == 1440:
        return "24:00"
    return f"{minutos // 60:02d}:{minutos % 60:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    if type(ocupados) is not list:
        raise TypeError("ocupados deve ser uma list")

    inicio_min = _minutos(inicio)
    fim_min = _minutos(fim)
    if inicio_min >= fim_min:
        raise ValueError("inicio deve ser anterior a fim")

    recortados: list[tuple[int, int]] = []
    for item in ocupados:
        if type(item) not in (tuple, list) or len(item) != 2:
            raise TypeError("cada intervalo deve ser um tuple ou list de dois horários")

        ini = _minutos(item[0])
        fim_item = _minutos(item[1])
        if ini > fim_item:
            raise ValueError("o início do intervalo deve ser menor ou igual ao fim")
        if ini == fim_item:
            continue

        ini_recortado = max(ini, inicio_min)
        fim_recortado = min(fim_item, fim_min)
        if ini_recortado < fim_recortado:
            recortados.append((ini_recortado, fim_recortado))

    recortados.sort()
    unidos: list[list[int]] = []
    for ini, fim_item in recortados:
        if unidos and ini <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], fim_item)
        else:
            unidos.append([ini, fim_item])

    livres: list[tuple[str, str]] = []
    cursor = inicio_min
    for ini, fim_item in unidos:
        if cursor < ini:
            livres.append((_formatar(cursor), _formatar(ini)))
        cursor = max(cursor, fim_item)

    if cursor < fim_min:
        livres.append((_formatar(cursor), _formatar(fim_min)))

    return livres
