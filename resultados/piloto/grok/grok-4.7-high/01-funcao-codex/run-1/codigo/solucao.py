def unir_intervalos(intervalos) -> list[tuple[int, int]]:
    pares: list[tuple[int, int]] = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError("início maior que fim")
        pares.append((inicio, fim))

    pares.sort()

    unidos: list[tuple[int, int]] = []
    for inicio, fim in pares:
        if unidos and inicio <= unidos[-1][1]:
            if fim > unidos[-1][1]:
                unidos[-1] = (unidos[-1][0], fim)
        else:
            unidos.append((inicio, fim))
    return unidos
