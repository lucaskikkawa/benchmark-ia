def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    """Une intervalos fechados de inteiros, opcionalmente recortados por `limites`."""
    if limites is not None:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError("limites invertidos")

    pares = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError(f"intervalo invalido: ({inicio!r}, {fim!r})")
        pares.append((inicio, fim))

    if limites is not None:
        recortados = []
        for inicio, fim in pares:
            inicio = max(inicio, minimo)
            fim = min(fim, maximo)
            if inicio <= fim:
                recortados.append((inicio, fim))
        pares = recortados

    pares.sort()
    resultado = []
    for inicio, fim in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fim > resultado[-1][1]:
                resultado[-1] = (resultado[-1][0], fim)
        else:
            resultado.append((inicio, fim))
    return resultado
