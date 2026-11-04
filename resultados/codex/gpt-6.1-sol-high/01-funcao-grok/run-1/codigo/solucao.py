"""Cálculo de intervalos livres em uma janela de um único dia."""


def _minutos(horario: str) -> int:
    if not isinstance(horario, str):
        raise TypeError("O horário deve ser uma string.")
    if (
        len(horario) != 5
        or horario[2] != ":"
        or any(c not in "0123456789" for c in horario[:2] + horario[3:])
    ):
        raise ValueError("Horário inválido: use HH:MM com dígitos ASCII.")

    horas = int(horario[:2])
    minutos = int(horario[3:])
    if horas > 24 or minutos > 59 or (horas == 24 and minutos != 0):
        raise ValueError("Horário fora dos limites do dia.")
    return horas * 60 + minutos


def _horario(minutos: int) -> str:
    horas, resto = divmod(minutos, 60)
    return f"{horas:02d}:{resto:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    if type(ocupados) is not list:
        raise TypeError("ocupados deve ser exatamente uma list.")

    inicio_janela = _minutos(inicio)
    fim_janela = _minutos(fim)
    if inicio_janela >= fim_janela:
        raise ValueError("O início da janela deve ser anterior ao fim.")

    recortados = []
    for par in ocupados:
        if not isinstance(par, (tuple, list)) or len(par) != 2:
            raise TypeError("Cada intervalo deve ser um par em tuple ou list.")
        inicio_ocupado = _minutos(par[0])
        fim_ocupado = _minutos(par[1])
        if inicio_ocupado > fim_ocupado:
            raise ValueError("O início de um ocupado não pode ser posterior ao fim.")
        if inicio_ocupado == fim_ocupado:
            continue

        inicio_recorte = max(inicio_janela, inicio_ocupado)
        fim_recorte = min(fim_janela, fim_ocupado)
        if inicio_recorte < fim_recorte:
            recortados.append((inicio_recorte, fim_recorte))

    recortados.sort()
    livres = []
    cursor = inicio_janela
    # O cursor acumula a união dos ocupados sobrepostos ou encostados.
    for inicio_ocupado, fim_ocupado in recortados:
        if cursor < inicio_ocupado:
            livres.append((_horario(cursor), _horario(inicio_ocupado)))
        cursor = max(cursor, fim_ocupado)
    if cursor < fim_janela:
        livres.append((_horario(cursor), _horario(fim_janela)))
    return livres
