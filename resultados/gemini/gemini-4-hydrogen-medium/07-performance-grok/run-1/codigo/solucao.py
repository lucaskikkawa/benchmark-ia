def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser uma list")
    if not isinstance(alvo, int) or isinstance(alvo, bool):
        raise TypeError("alvo deve ser int")

    vistos: dict[int, int] = {}
    total = 0
    for x in nums:
        if not isinstance(x, int) or isinstance(x, bool):
            raise TypeError("todos os elementos de nums devem ser int")
        total += vistos.get(alvo - x, 0)
        vistos[x] = vistos.get(x, 0) + 1
    return total
