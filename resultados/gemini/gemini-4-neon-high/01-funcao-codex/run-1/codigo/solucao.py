def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    """Une intervalos fechados de inteiros, com recorte opcional por limites."""
    if limites is not None:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError(f"Limites invertidos: ({minimo}, {maximo})")

    filtrados: list[tuple[int, int]] = []
    if limites is None:
        for inicio, fim in intervalos:
            if inicio > fim:
                raise ValueError(f"Intervalo invertido: ({inicio}, {fim})")
            filtrados.append((inicio, fim))
    else:
        for inicio, fim in intervalos:
            if inicio > fim:
                raise ValueError(f"Intervalo invertido: ({inicio}, {fim})")
            if fim < minimo or inicio > maximo:
                continue
            if inicio < minimo:
                inicio = minimo
            if fim > maximo:
                fim = maximo
            filtrados.append((inicio, fim))

    if not filtrados:
        return []

    filtrados.sort()

    resultado: list[tuple[int, int]] = []
    it = iter(filtrados)
    atual_inicio, atual_fim = next(it)

    for inicio, fim in it:
        if inicio <= atual_fim:
            if fim > atual_fim:
                atual_fim = fim
        else:
            resultado.append((atual_inicio, atual_fim))
            atual_inicio = inicio
            atual_fim = fim

    resultado.append((atual_inicio, atual_fim))
    return resultado
