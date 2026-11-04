def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
    if type(nums) is not list:
        raise TypeError("nums deve ser uma lista")
    if type(alvo) is bool or not isinstance(alvo, int):
        raise TypeError("alvo deve ser um int (bool não é permitido)")

    total = 0
    freq: dict[int, int] = {}
    for x in nums:
        if type(x) is bool or not isinstance(x, int):
            raise TypeError("todos os elementos de nums devem ser int (bool não é permitido)")
        comp = alvo - x
        if comp in freq:
            total += freq[comp]
        freq[x] = freq.get(x, 0) + 1

    return total
