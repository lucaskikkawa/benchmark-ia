def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    """Une intervalos fechados que se sobrepõem ou compartilham extremidades.

    Args:
        intervalos: Iterável finito de pares de inteiros (inicio, fim) com inicio <= fim.
        limites: Par opcional (minimo, maximo) para recortar os intervalos antes da união.

    Returns:
        Lista de tuplas (inicio, fim) ordenada por início representando a união.

    Raises:
        ValueError: Se limites estiverem invertidos (minimo > maximo) ou se qualquer
            par original tiver inicio > fim.
    """
    if limites is not None:
        lim_min, lim_max = limites
        if lim_min > lim_max:
            raise ValueError(f"Limites invertidos: ({lim_min}, {lim_max})")

    coletados = []
    for par in intervalos:
        inicio, fim = par
        if inicio > fim:
            raise ValueError(f"Intervalo com início maior que fim: ({inicio}, {fim})")
        if limites is not None:
            recorte_inicio = max(inicio, lim_min)
            recorte_fim = min(fim, lim_max)
            if recorte_inicio <= recorte_fim:
                coletados.append((recorte_inicio, recorte_fim))
        else:
            coletados.append((inicio, fim))

    if not coletados:
        return []

    coletados.sort()

    resultado: list[tuple[int, int]] = []
    for inicio, fim in coletados:
        if not resultado:
            resultado.append((inicio, fim))
        else:
            ultimo_inicio, ultimo_fim = resultado[-1]
            if inicio <= ultimo_fim:
                if fim > ultimo_fim:
                    resultado[-1] = (ultimo_inicio, fim)
            else:
                resultado.append((inicio, fim))

    return resultado
