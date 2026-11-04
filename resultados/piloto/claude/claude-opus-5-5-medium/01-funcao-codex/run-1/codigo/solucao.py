def unir_intervalos(intervalos) -> list[tuple[int, int]]:
    pares = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError(f"intervalo inválido: ({inicio!r}, {fim!r})")
        pares.append((inicio, fim))
    pares.sort()

    resultado: list[tuple[int, int]] = []
    for inicio, fim in pares:
        if resultado and inicio <= resultado[-1][1]:
            if fim > resultado[-1][1]:
                resultado[-1] = (resultado[-1][0], fim)
        else:
            resultado.append((inicio, fim))
    return resultado
