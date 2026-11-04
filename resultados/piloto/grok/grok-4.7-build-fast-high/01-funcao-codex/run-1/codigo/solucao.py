def unir_intervalos(intervalos) -> list[tuple[int, int]]:
    """Une intervalos fechados que se sobrepõem ou compartilham uma extremidade.

    A lista resultante fica ordenada pelo início. Intervalos separados por uma
    unidade permanecem distintos. Não altera a coleção recebida.
    """
    pares = [(inicio, fim) for inicio, fim in intervalos]
    for inicio, fim in pares:
        if inicio > fim:
            raise ValueError("início maior que o fim")
    if not pares:
        return []

    pares.sort()
    uniao: list[tuple[int, int]] = []
    atual_inicio, atual_fim = pares[0]
    for inicio, fim in pares[1:]:
        if inicio <= atual_fim:
            if fim > atual_fim:
                atual_fim = fim
        else:
            uniao.append((atual_inicio, atual_fim))
            atual_inicio, atual_fim = inicio, fim
    uniao.append((atual_inicio, atual_fim))
    return uniao
