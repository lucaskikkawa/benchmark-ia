def unir_intervalos(intervalos) -> list[tuple[int, int]]:
    """Retorne a união ordenada de intervalos fechados, sem alterar a entrada."""
    ordenados = []
    for inicio, fim in intervalos:
        if inicio > fim:
            raise ValueError("início maior que fim")
        ordenados.append((inicio, fim))
    ordenados.sort()
    resultado = []
    for inicio, fim in ordenados:
        if resultado and inicio <= resultado[-1][1]:
            anterior, limite = resultado[-1]
            resultado[-1] = (anterior, max(limite, fim))
        else:
            resultado.append((inicio, fim))
    return resultado
