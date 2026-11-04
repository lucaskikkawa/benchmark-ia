"""Cálculo de intervalos livres em uma janela diária."""


def _minutos(horario: str) -> int:
    """Valida um horário HH:MM e o converte em minutos desde meia-noite."""
    if not isinstance(horario, str):
        raise TypeError("horário deve ser str")
    if (
        len(horario) != 5
        or horario[2] != ":"
        or any(caractere not in "0123456789" for caractere in horario[:2] + horario[3:])
    ):
        raise ValueError("horário inválido")

    hora = (ord(horario[0]) - 48) * 10 + ord(horario[1]) - 48
    minuto = (ord(horario[3]) - 48) * 10 + ord(horario[4]) - 48
    if minuto > 59 or hora > 24 or (hora == 24 and minuto != 0):
        raise ValueError("horário inválido")
    return hora * 60 + minuto


def _formatar(minutos: int) -> str:
    if minutos == 1440:
        return "24:00"
    hora, minuto = divmod(minutos, 60)
    return f"{hora:02d}:{minuto:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Devolve os intervalos livres dentro da janela semiaberta [inicio, fim)."""
    janela_inicio = _minutos(inicio)
    janela_fim = _minutos(fim)
    if janela_inicio >= janela_fim:
        raise ValueError("inicio deve ser anterior a fim")

    if type(ocupados) is not list:
        raise TypeError("ocupados deve ser uma list")

    recortados: list[tuple[int, int]] = []
    for item in ocupados:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise TypeError("cada ocupado deve ser um par (ini, fim)")

        ini = _minutos(item[0])
        termino = _minutos(item[1])
        if ini > termino:
            raise ValueError("o início do ocupado deve ser menor ou igual ao fim")
        if ini == termino:
            continue

        recorte_ini = max(ini, janela_inicio)
        recorte_fim = min(termino, janela_fim)
        if recorte_ini < recorte_fim:
            recortados.append((recorte_ini, recorte_fim))

    recortados.sort()
    unidos: list[list[int]] = []
    for ini, termino in recortados:
        if unidos and ini <= unidos[-1][1]:
            unidos[-1][1] = max(unidos[-1][1], termino)
        else:
            unidos.append([ini, termino])

    livres: list[tuple[str, str]] = []
    cursor = janela_inicio
    for ini, termino in unidos:
        if cursor < ini:
            livres.append((_formatar(cursor), _formatar(ini)))
        cursor = max(cursor, termino)
    if cursor < janela_fim:
        livres.append((_formatar(cursor), _formatar(janela_fim)))
    return livres
