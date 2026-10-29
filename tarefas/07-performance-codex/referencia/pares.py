def contar_pares(valores, alvo: int) -> int:
    """Conte pares de índices i < j com soma alvo em uma única passagem."""
    frequencias = {}
    total = 0
    for valor in valores:
        total += frequencias.get(alvo - valor, 0)
        frequencias[valor] = frequencias.get(valor, 0) + 1
    return total
