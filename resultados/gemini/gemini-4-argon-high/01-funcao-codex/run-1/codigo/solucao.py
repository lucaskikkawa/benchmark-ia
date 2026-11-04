def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    if limites is not None:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError("Limites invertidos: minimo maior que maximo.")

    processados: list[tuple[int, int]] = []

    if limites is None:
        for inicio, fim in intervalos:
            if inicio > fim:
                raise ValueError("Intervalo invertido: inicio maior que fim.")
            processados.append((inicio, fim))
    else:
        for inicio, fim in intervalos:
            if inicio > fim:
                raise ValueError("Intervalo invertido: inicio maior que fim.")
            rec_ini = minimo if inicio < minimo else inicio
            rec_fim = maximo if fim > maximo else fim
            if rec_ini <= rec_fim:
                processados.append((rec_ini, rec_fim))

    if not processados:
        return []

    processados.sort()

    resultado: list[tuple[int, int]] = []
    it = iter(processados)
    atual_ini, atual_fim = next(it)

    for ini, fim in it:
        if ini <= atual_fim:
            if fim > atual_fim:
                atual_fim = fim
        else:
            resultado.append((atual_ini, atual_fim))
            atual_ini, atual_fim = ini, fim

    resultado.append((atual_ini, atual_fim))
    return resultado
