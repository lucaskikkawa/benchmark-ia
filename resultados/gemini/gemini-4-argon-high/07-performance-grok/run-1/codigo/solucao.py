from collections import Counter


def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser list")
    if not isinstance(alvo, int) or isinstance(alvo, bool):
        raise TypeError("alvo deve ser int")
    for x in nums:
        if not isinstance(x, int) or isinstance(x, bool):
            raise TypeError("elementos de nums devem ser int")

    if len(nums) < 2:
        return 0

    freq = Counter(nums)
    total = 0
    for x, c in freq.items():
        y = alvo - x
        if x < y:
            total += c * freq.get(y, 0)
        elif x == y:
            total += c * (c - 1) // 2
    return total
