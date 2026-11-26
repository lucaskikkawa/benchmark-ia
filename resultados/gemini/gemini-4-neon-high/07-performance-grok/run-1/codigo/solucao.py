def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser uma list.")
    if type(alvo) is not int and (isinstance(alvo, bool) or not isinstance(alvo, int)):
        raise TypeError("alvo deve ser um int.")

    vistos: dict[int, int] = {}
    vistos_get = vistos.get
    total = 0

    for x in nums:
        if type(x) is not int and (isinstance(x, bool) or not isinstance(x, int)):
            raise TypeError("Todos os elementos de nums devem ser int.")
        total += vistos_get(alvo - x, 0)
        vistos[x] = vistos_get(x, 0) + 1

    return total
