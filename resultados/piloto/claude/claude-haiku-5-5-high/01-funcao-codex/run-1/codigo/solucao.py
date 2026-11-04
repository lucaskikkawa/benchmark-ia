def unir_intervalos(intervalos) -> list[tuple[int, int]]:
    pares = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError(f"intervalo inválido: ({inicio}, {fim})")
        pares.append((inicio, fim))

    pares.sort()

    uniao = []
    for inicio, fim in pares:
        if uniao and inicio <= uniao[-1][1]:
            inicio_atual, fim_atual = uniao[-1]
            uniao[-1] = (inicio_atual, max(fim_atual, fim))
        else:
            uniao.append((inicio, fim))
    return uniao
