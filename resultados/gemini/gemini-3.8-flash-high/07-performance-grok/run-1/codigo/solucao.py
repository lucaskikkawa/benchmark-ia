def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser uma lista")
    if isinstance(alvo, bool) or not isinstance(alvo, int):
        raise TypeError("alvo deve ser um número inteiro")

    freq: dict[int, int] = {}
    total = 0
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int):
            raise TypeError("todos os elementos de nums devem ser números inteiros")
        comp = alvo - x
        if comp in freq:
            total += freq[comp]
        freq[x] = freq.get(x, 0) + 1

    return total
