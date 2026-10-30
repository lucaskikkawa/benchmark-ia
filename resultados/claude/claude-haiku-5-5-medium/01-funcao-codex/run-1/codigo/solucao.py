def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    # Materializa a entrada uma única vez: aceita geradores e não altera o original.
    pares = list(intervalos)

    # Valida todos os pares originais, inclusive os que serão descartados pelo recorte.
    for inicio, fim in pares:
        if inicio > fim:
            raise ValueError(f"intervalo invertido: ({inicio}, {fim})")

    if limites is not None:
        minimo, maximo = limites
        if minimo > maximo:
            raise ValueError(f"limites invertidos: ({minimo}, {maximo})")

        recortados = []
        for inicio, fim in pares:
            # Extremidades do recorte são retidas (inclusive); intersecção vazia é descartada.
            nova_inicio = max(inicio, minimo)
            nova_fim = min(fim, maximo)
            if nova_inicio <= nova_fim:
                recortados.append((nova_inicio, nova_fim))
        pares = recortados

    # Ordena por início e varre fundindo sobreposições e extremidades compartilhadas.
    # Intervalos separados por uma unidade (fim=2, início=3) NÃO se fundem.
    pares.sort()
    resultado: list[tuple[int, int]] = []
    for inicio, fim in pares:
        if resultado and inicio <= resultado[-1][1]:
            ultimo_inicio, ultimo_fim = resultado[-1]
            resultado[-1] = (ultimo_inicio, max(ultimo_fim, fim))
        else:
            resultado.append((inicio, fim))
    return resultado
