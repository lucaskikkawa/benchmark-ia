def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    """Une intervalos fechados de inteiros, com recorte opcional.

    Intervalos que se sobrepõem ou que compartilham uma extremidade são fundidos.
    Intervalos separados por ao menos uma unidade permanecem distintos.
    """
    if limites is not None:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError("limites invertidos")

    preparados: list[tuple[int, int]] = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError("inicio maior que fim")
        if limites is not None:
            a = max(inicio, minimo)
            b = min(fim, maximo)
            if a > b:
                continue
            preparados.append((a, b))
        else:
            preparados.append((inicio, fim))

    if not preparados:
        return []

    preparados.sort()
    uniao: list[tuple[int, int]] = []
    atual_inicio, atual_fim = preparados[0]
    for inicio, fim in preparados[1:]:
        if inicio <= atual_fim:
            if fim > atual_fim:
                atual_fim = fim
        else:
            uniao.append((atual_inicio, atual_fim))
            atual_inicio, atual_fim = inicio, fim
    uniao.append((atual_inicio, atual_fim))
    return uniao
