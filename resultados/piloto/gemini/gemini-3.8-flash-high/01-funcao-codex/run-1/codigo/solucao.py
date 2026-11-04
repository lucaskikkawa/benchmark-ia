def unir_intervalos(intervalos) -> list[tuple[int, int]]:
    """Une intervalos fechados que se sobrepõem ou compartilham extremidades.

    Recebe um iterável finito de pares (inicio, fim) com inicio <= fim.
    Retorna uma lista de tuplas ordenada pelo início com os intervalos unidos.
    Lança ValueError se algum par tiver inicio > fim.
    """
    lista: list[tuple[int, int]] = []
    for item in intervalos:
        inicio, fim = item
        if inicio > fim:
            raise ValueError(f"Intervalo inválido: início ({inicio}) maior que fim ({fim})")
        lista.append((int(inicio), int(fim)))

    if not lista:
        return []

    lista.sort()

    resultado: list[tuple[int, int]] = []
    for inicio, fim in lista:
        if not resultado:
            resultado.append((inicio, fim))
        else:
            ult_inicio, ult_fim = resultado[-1]
            if inicio <= ult_fim:
                resultado[-1] = (ult_inicio, max(ult_fim, fim))
            else:
                resultado.append((inicio, fim))

    return resultado
