def unir_intervalos(intervalos) -> list[tuple[int, int]]:
    """Devolve a união de intervalos fechados [inicio, fim], ordenada por início.

    Intervalos que se sobrepõem ou compartilham uma extremidade são fundidos;
    intervalos separados por pelo menos uma unidade não são.
    """
    pares = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError(f"intervalo inválido: ({inicio}, {fim})")
        pares.append((inicio, fim))

    pares.sort()
    resultado = []
    for inicio, fim in pares:
        if resultado and inicio <= resultado[-1][1]:
            ultimo_inicio, ultimo_fim = resultado[-1]
            resultado[-1] = (ultimo_inicio, max(ultimo_fim, fim))
        else:
            resultado.append((inicio, fim))
    return resultado
