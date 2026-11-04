def unir_intervalos(intervalos) -> list[tuple[int, int]]:
    pares: list[tuple[int, int]] = []
    for item in intervalos:
        inicio, fim = item
        if inicio > fim:
            raise ValueError(f"Intervalo inválido: início ({inicio}) maior que fim ({fim})")
        pares.append((inicio, fim))

    if not pares:
        return []

    pares.sort(key=lambda p: (p[0], p[1]))

    resultado: list[tuple[int, int]] = []
    cur_inicio, cur_fim = pares[0]

    for inicio, fim in pares[1:]:
        if inicio <= cur_fim:
            if fim > cur_fim:
                cur_fim = fim
        else:
            resultado.append((cur_inicio, cur_fim))
            cur_inicio, cur_fim = inicio, fim

    resultado.append((cur_inicio, cur_fim))
    return resultado
