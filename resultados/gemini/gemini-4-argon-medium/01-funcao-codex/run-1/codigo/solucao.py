def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    if limites is not None:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError("Limites invertidos: minimo > maximo")

    processados: list[tuple[int, int]] = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError("Intervalo invertido: inicio > fim")
        if limites is not None:
            rec_inicio = inicio if inicio > minimo else minimo
            rec_fim = fim if fim < maximo else maximo
            if rec_inicio <= rec_fim:
                processados.append((rec_inicio, rec_fim))
        else:
            processados.append((inicio, fim))

    if not processados:
        return []

    processados.sort()

    resultado: list[tuple[int, int]] = []
    atual_inicio, atual_fim = processados[0]

    for inicio, fim in processados[1:]:
        if inicio <= atual_fim:
            if fim > atual_fim:
                atual_fim = fim
        else:
            resultado.append((atual_inicio, atual_fim))
            atual_inicio, atual_fim = inicio, fim

    resultado.append((atual_inicio, atual_fim))
    return resultado
