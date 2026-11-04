def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Conte pares de índices i < j cuja soma é alvo, sem alterar nums."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser uma lista")
    if not isinstance(alvo, int) or isinstance(alvo, bool):
        raise TypeError("alvo deve ser um int, exceto bool")

    frequencias: dict[int, int] = {}
    total = 0
    for numero in nums:
        if not isinstance(numero, int) or isinstance(numero, bool):
            raise TypeError("cada elemento de nums deve ser um int, exceto bool")
        total += frequencias.get(alvo - numero, 0)
        frequencias[numero] = frequencias.get(numero, 0) + 1
    return total
