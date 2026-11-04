def contar_pares(valores, alvo: int) -> int:
    """Conta pares i < j com valores[i] + valores[j] == alvo.

    Uma passagem: para cada valor, soma a frequência já vista do complemento
    e só então registra o valor. Tempo O(n), memória O(k).
    """
    frequencias = {}
    total = 0
    for valor in valores:
        total += frequencias.get(alvo - valor, 0)
        frequencias[valor] = frequencias.get(valor, 0) + 1
    return total
