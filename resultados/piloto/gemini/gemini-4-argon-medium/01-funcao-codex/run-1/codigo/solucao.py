def unir_intervalos(intervalos) -> list[tuple[int, int]]:
    pares: list[tuple[int, int]] = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError(f"Intervalo inválido: ({inicio}, {fim})")
        pares.append((inicio, fim))

    if not pares:
        return []

    pares.sort()
    resultado: list[tuple[int, int]] = [pares[0]]

    for inicio, fim in pares[1:]:
        ultimo_inicio, ultimo_fim = resultado[-1]
        if inicio <= ultimo_fim:
            if fim > ultimo_fim:
                resultado[-1] = (ultimo_inicio, fim)
        else:
            resultado.append((inicio, fim))

    return resultado
