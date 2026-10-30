def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    """Une intervalos fechados, com recorte opcional em ``limites``.

    Intervalos que se sobrepõem ou compartilham uma extremidade são fundidos.
    Um vão de pelo menos uma unidade permanece separado. ``limites``, quando
    informado, é o recorte fechado ``(minimo, maximo)`` aplicado antes da união.
    """
    if limites is not None:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError("limites invertidos")

    preparados: list[tuple[int, int]] = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError("intervalo invertido")
        if limites is not None:
            if inicio < minimo:
                inicio = minimo
            if fim > maximo:
                fim = maximo
            if inicio > fim:
                continue
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
