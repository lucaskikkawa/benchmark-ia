def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    """Une intervalos fechados, fundindo os que se tocam ou se sobrepõem.

    Com ``limites=(minimo, maximo)``, cada intervalo é interseccionado com
    esse recorte fechado antes da união. Pares invertidos e limites invertidos
    lançam ``ValueError``. A lista de entrada não é alterada.
    """
    recortar = limites is not None
    if recortar:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError("limites invertidos")

    preparados: list[tuple[int, int]] = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError("intervalo com início maior que o fim")
        if recortar:
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
    for indice in range(1, len(preparados)):
        inicio, fim = preparados[indice]
        if inicio <= atual_fim:
            if fim > atual_fim:
                atual_fim = fim
        else:
            uniao.append((atual_inicio, atual_fim))
            atual_inicio, atual_fim = inicio, fim
    uniao.append((atual_inicio, atual_fim))
    return uniao
