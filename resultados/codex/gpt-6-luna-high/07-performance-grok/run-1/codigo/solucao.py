def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Retorna a quantidade de pares de índices i < j cuja soma é alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser uma lista")
    if isinstance(alvo, bool) or not isinstance(alvo, int):
        raise TypeError("alvo deve ser um int")

    frequencias: dict[int, int] = {}
    total = 0
    for numero in nums:
        if isinstance(numero, bool) or not isinstance(numero, int):
            raise TypeError("cada elemento de nums deve ser um int")
        complemento = alvo - numero
        total += frequencias.get(complemento, 0)
        frequencias[numero] = frequencias.get(numero, 0) + 1

    return total
