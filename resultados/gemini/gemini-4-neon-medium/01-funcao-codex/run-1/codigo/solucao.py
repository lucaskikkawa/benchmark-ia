from collections.abc import Iterable


def unir_intervalos(
    intervalos: Iterable[tuple[int, int]],
    *,
    limites: tuple[int, int] | None = None,
) -> list[tuple[int, int]]:
    """Une intervalos fechados de inteiros, com recorte opcional por limites."""
    if limites is not None:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError("limites invertidos: minimo > maximo")
    else:
        minimo = maximo = 0

    normalizados: list[tuple[int, int]] = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError("intervalo invertido: inicio > fim")
        if limites is not None:
            if fim < minimo or inicio > maximo:
                continue
            if inicio < minimo:
                inicio = minimo
            if fim > maximo:
                fim = maximo
        normalizados.append((inicio, fim))

    if not normalizados:
        return []

    normalizados.sort()

    it = iter(normalizados)
    atual_inicio, atual_fim = next(it)
    resultado: list[tuple[int, int]] = []

    for inicio, fim in it:
        if inicio <= atual_fim:
            if fim > atual_fim:
                atual_fim = fim
        else:
            resultado.append((atual_inicio, atual_fim))
            atual_inicio, atual_fim = inicio, fim

    resultado.append((atual_inicio, atual_fim))
    return resultado
