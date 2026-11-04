def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    """Une intervalos fechados [inicio, fim] de inteiros.

    Intervalos que se sobrepõem ou compartilham uma extremidade são fundidos;
    intervalos separados por uma unidade não são fundidos.
    Se `limites` for (minimo, maximo), cada intervalo é recortado antes da união.
    """
    # Materializa a entrada: aceita geradores consumidos uma única vez
    # e garante que a lista recebida não seja modificada.
    pares = list(intervalos)
    for inicio, fim in pares:
        if inicio > fim:
            raise ValueError(f"intervalo invertido: ({inicio}, {fim})")

    if limites is not None:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError(f"limites invertidos: ({minimo}, {maximo})")

        recortados = []
        for inicio, fim in pares:
            # Extremidades do recorte são retidas (comparação inclusiva).
            novo_inicio = max(inicio, minimo)
            novo_fim = min(fim, maximo)
            if novo_inicio <= novo_fim:
                recortados.append((novo_inicio, novo_fim))
        pares = recortados

    # Ordenação + varredura: O(n log n) de tempo, O(n) de memória.
    pares.sort()
    resultado = []
    for inicio, fim in pares:
        if resultado and inicio <= resultado[-1][1]:
            ultimo_inicio, ultimo_fim = resultado[-1]
            if fim > ultimo_fim:
                resultado[-1] = (ultimo_inicio, fim)
        else:
            resultado.append((inicio, fim))
    return resultado
