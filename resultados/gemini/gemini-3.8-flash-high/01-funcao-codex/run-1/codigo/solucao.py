def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    """Une intervalos fechados que se sobrepõem ou compartilham extremidades.

    Parâmetros:
        intervalos: Iterável finito de pares de inteiros (inicio, fim).
        limites: Par opcional (minimo, maximo) de inteiros para recorte fechado.

    Retorna:
        Lista de tuplas (inicio, fim) representando a união ordenada por início.
    """
    min_lim = None
    max_lim = None
    if limites is not None:
        min_lim, max_lim = limites
        if min_lim > max_lim:
            raise ValueError(f"Limites invertidos: {min_lim} > {max_lim}")

    valid_intervals: list[tuple[int, int]] = []
    for pair in intervalos:
        inicio, fim = pair
        if inicio > fim:
            raise ValueError(f"Intervalo com início maior que fim: ({inicio}, {fim})")
        if min_lim is not None:
            c_inicio = max(inicio, min_lim)
            c_fim = min(fim, max_lim)
            if c_inicio <= c_fim:
                valid_intervals.append((c_inicio, c_fim))
        else:
            valid_intervals.append((inicio, fim))

    if not valid_intervals:
        return []

    valid_intervals.sort()

    merged: list[tuple[int, int]] = []
    it = iter(valid_intervals)
    curr_start, curr_end = next(it)

    for next_start, next_end in it:
        if next_start <= curr_end:
            if next_end > curr_end:
                curr_end = next_end
        else:
            merged.append((curr_start, curr_end))
            curr_start, curr_end = next_start, next_end

    merged.append((curr_start, curr_end))
    return merged
