def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    """Una intervalos fechados em O(n log n), com recorte opcional e sem mutação."""
    if limites is not None:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError("limites invertidos")
    ordenados = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError("início maior que fim")
        if limites is not None:
            inicio, fim = max(inicio, minimo), min(fim, maximo)
            if inicio > fim:
                continue
        ordenados.append((inicio, fim))
    ordenados.sort()
    resultado = []
    for inicio, fim in ordenados:
        if resultado and inicio <= resultado[-1][1]:
            anterior, limite = resultado[-1]
            resultado[-1] = (anterior, max(limite, fim))
        else:
            resultado.append((inicio, fim))
    return resultado
