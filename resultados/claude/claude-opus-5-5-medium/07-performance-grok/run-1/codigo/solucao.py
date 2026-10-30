from collections import Counter


def _eh_int(x) -> bool:
    return isinstance(x, int) and not isinstance(x, bool)


def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser list")
    if not _eh_int(alvo):
        raise TypeError("alvo deve ser int")
    for x in nums:
        if not _eh_int(x):
            raise TypeError("elementos de nums devem ser int")

    vistos: Counter = Counter()
    total = 0
    for x in nums:
        total += vistos.get(alvo - x, 0)
        vistos[x] += 1
    return total
