"""Cálculo de intervalos livres dentro de uma janela diária."""


def _minutos(horario: str) -> int:
    if not isinstance(horario, str):
        raise TypeError("O horário deve ser uma string.")
    if (
        len(horario) != 5
        or horario[2] != ":"
        or any(c not in "0123456789" for c in horario[:2] + horario[3:])
    ):
        raise ValueError("Horário inválido: esperado HH:MM com dígitos ASCII.")
    horas = int(horario[:2])
    minutos = int(horario[3:])
    if minutos > 59 or horas > 24 or (horas == 24 and minutos != 0):
        raise ValueError("Horário fora dos limites do dia.")
    return horas * 60 + minutos


def _horario(minutos: int) -> str:
    horas, minutos = divmod(minutos, 60)
    return f"{horas:02d}:{minutos:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    if type(ocupados) is not list:
        raise TypeError("Ocupados deve ser exatamente uma lista.")
    inicio_janela = _minutos(inicio)
    fim_janela = _minutos(fim)
    if inicio_janela >= fim_janela:
        raise ValueError("O início da janela deve ser anterior ao fim.")

    recortados = []
    for par in ocupados:
        if not isinstance(par, (tuple, list)) or len(par) != 2:
            raise TypeError("Cada ocupado deve ser um par de horários.")
        ini_ocupado = _minutos(par[0])
        fim_ocupado = _minutos(par[1])
        if ini_ocupado > fim_ocupado:
            raise ValueError("O início do ocupado não pode ser posterior ao fim.")
        ini_recortado = max(ini_ocupado, inicio_janela)
        fim_recortado = min(fim_ocupado, fim_janela)
        if ini_recortado < fim_recortado:
            recortados.append((ini_recortado, fim_recortado))

    recortados.sort()
    livres = []
    cursor = inicio_janela
    for ini_ocupado, fim_ocupado in recortados:
        if cursor < ini_ocupado:
            livres.append((_horario(cursor), _horario(ini_ocupado)))
        cursor = max(cursor, fim_ocupado)
    if cursor < fim_janela:
        livres.append((_horario(cursor), _horario(fim_janela)))
    return livres
