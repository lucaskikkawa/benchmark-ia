from collections import Counter


def _eh_int(valor: object) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool)


def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser list")
    if not _eh_int(alvo):
        raise TypeError("alvo deve ser int")
    for x in nums:
        if not _eh_int(x):
            raise TypeError("cada elemento de nums deve ser int")

    freq = Counter(nums)
    total = 0
    for x, fx in freq.items():
        y = alvo - x
        if x == y:
            total += fx * (fx - 1) // 2
        elif x < y:
            total += fx * freq.get(y, 0)
    return total
