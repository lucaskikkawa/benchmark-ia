def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser list")
    if type(alvo) is not int:
        raise TypeError("alvo deve ser int")

    freq: dict[int, int] = {}
    for x in nums:
        if type(x) is not int:
            raise TypeError("todos os elementos devem ser int")
        freq[x] = freq.get(x, 0) + 1

    total = 0
    for x, fx in freq.items():
        y = alvo - x
        if x == y:
            # 2 * x == alvo: pares dentro do mesmo valor
            total += fx * (fx - 1) // 2
        elif x < y and y in freq:
            # cada valor entra uma vez, evitando contar o par duas vezes
            total += fx * freq[y]
    return total
