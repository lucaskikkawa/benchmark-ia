def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser uma list")
    if type(alvo) is not int and (not isinstance(alvo, int) or isinstance(alvo, bool)):
        raise TypeError("alvo deve ser int")

    visto: dict[int, int] = {}
    total = 0
    for x in nums:
        if type(x) is not int and (not isinstance(x, int) or isinstance(x, bool)):
            raise TypeError("todos os elementos de nums devem ser int")
        comp = alvo - x
        if comp in visto:
            total += visto[comp]
        visto[x] = visto.get(x, 0) + 1

    return total
