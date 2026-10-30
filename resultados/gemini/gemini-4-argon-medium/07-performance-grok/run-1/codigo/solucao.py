def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser uma list")
    if isinstance(alvo, bool) or not isinstance(alvo, int):
        raise TypeError("alvo deve ser um int")

    freq: dict[int, int] = {}
    for x in nums:
        if isinstance(x, bool) or not isinstance(x, int):
            raise TypeError("todos os elementos de nums devem ser int")
        freq[x] = freq.get(x, 0) + 1

    total = 0
    for x, c in freq.items():
        comp = alvo - x
        if comp < x:
            continue
        if comp == x:
            total += c * (c - 1) // 2
        else:
            c2 = freq.get(comp, 0)
            if c2:
                total += c * c2

    return total
