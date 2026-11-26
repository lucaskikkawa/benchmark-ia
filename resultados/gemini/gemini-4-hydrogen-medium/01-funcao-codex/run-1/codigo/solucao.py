from __future__ import annotations

from collections.abc import Iterable


def unir_intervalos(
    intervalos: Iterable[tuple[int, int]],
    *,
    limites: tuple[int, int] | None = None,
) -> list[tuple[int, int]]:
    """Une intervalos fechados de inteiros, opcionalmente recortados por limites.

    Cada par (inicio, fim) deve satisfazer inicio <= fim; caso contrário, ou se
    limites=(minimo, maximo) tiver minimo > maximo, lança ValueError.
    """
    if limites is not None:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError("limites inválidos: minimo > maximo")
    else:
        minimo = maximo = None

    validos: list[tuple[int, int]] = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError("intervalo inválido: inicio > fim")
        if minimo is not None:
            if fim < minimo or inicio > maximo:
                continue
            if inicio < minimo:
                inicio = minimo
            if fim > maximo:
                fim = maximo
        validos.append((inicio, fim))

    if not validos:
        return []

    validos.sort()

    resultado: list[tuple[int, int]] = []
    atual_inicio, atual_fim = validos[0]

    for inicio, fim in validos[1:]:
        if inicio <= atual_fim:
            if fim > atual_fim:
                atual_fim = fim
        else:
            resultado.append((atual_inicio, atual_fim))
            atual_inicio, atual_fim = inicio, fim

    resultado.append((atual_inicio, atual_fim))
    return resultado
