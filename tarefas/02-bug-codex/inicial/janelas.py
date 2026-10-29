def somas_janelas(valores: list[int], tamanho: int) -> list[int]:
    """Calcule somas de janelas contíguas de tamanho fixo."""
    if tamanho <= 0:
        raise ValueError("tamanho deve ser positivo")
    if tamanho > len(valores):
        return []
    soma = sum(valores[:tamanho])
    resultado = [soma]
    for indice in range(tamanho, len(valores) - 1):
        soma += valores[indice] - valores[indice - tamanho]
        resultado.append(soma)
    return resultado
