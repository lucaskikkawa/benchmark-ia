def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares de índices i < j cuja soma é alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums tem de ser uma list")
    if type(alvo) is not int:
        raise TypeError("alvo tem de ser int")

    frequencias: dict[int, int] = {}
    total = 0
    for numero in nums:
        if type(numero) is not int:
            raise TypeError("cada elemento de nums tem de ser int")
        total += frequencias.get(alvo - numero, 0)
        frequencias[numero] = frequencias.get(numero, 0) + 1
    return total
