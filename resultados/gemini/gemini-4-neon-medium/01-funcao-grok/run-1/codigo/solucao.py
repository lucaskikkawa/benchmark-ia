"""Cálculo de intervalos livres dentro de uma janela de horários."""

from __future__ import annotations

_ASCII_DIGITS = frozenset("0123456789")


def _parse_hora(valor: object) -> int:
    if not isinstance(valor, str):
        raise TypeError(f"Horário deve ser str, recebido {type(valor).__name__}.")
    if (
        len(valor) != 5
        or valor[2] != ":"
        or valor[0] not in _ASCII_DIGITS
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
        return 1440

    if horas > 23 or minutos > 59:
        raise ValueError(f"Horário inválido: {valor!r}.")

    return horas * 60 + minutos


def _formatar_hora(minutos_totais: int) -> str:
    horas, minutos = divmod(minutos_totais, 60)
    return f"{horas:02d}:{minutos:02d}"


def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
    if type(ocupados) is not list:
        raise TypeError(f"ocupados deve ser list, recebido {type(ocupados).__name__}.")

    win_ini = _parse_hora(inicio)
    win_fim = _parse_hora(fim)
    if win_ini >= win_fim:
        raise ValueError("inicio deve ser estritamente anterior a fim.")

    recortados: list[tuple[int, int]] = []
    for item in ocupados:
        if not isinstance(item, (tuple, list)) or len(item) != 2:
            raise TypeError(
                "Cada item de ocupados deve ser tuple ou list de exatamente 2 strings."
            )
        ini = _parse_hora(item[0])
        fim_item = _parse_hora(item[1])
        if ini > fim_item:
            raise ValueError(
                f"Intervalo invertido em ocupados: ({item[0]!r}, {item[1]!r})."
            )
        if ini == fim_item:
            continue

        c_ini = ini if ini > win_ini else win_ini
        c_fim = fim_item if fim_item < win_fim else win_fim
        if c_ini < c_fim:
            recortados.append((c_ini, c_fim))

    recortados.sort()

    unidos: list[tuple[int, int]] = []
    for c_ini, c_fim in recortados:
        if unidos and c_ini <= unidos[-1][1]:
            if c_fim > unidos[-1][1]:
                unidos[-1] = (unidos[-1][0], c_fim)
        else:
            unidos.append((c_ini, c_fim))

    livres: list[tuple[str, str]] = []
    cursor = win_ini
    for b_ini, b_fim in unidos:
        if cursor < b_ini:
            livres.append((_formatar_hora(cursor), _formatar_hora(b_ini)))
        cursor = b_fim
    if cursor < win_fim:
        livres.append((_formatar_hora(cursor), _formatar_hora(win_fim)))

    return livres
