def _eh_int(valor) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool)


def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
    if not isinstance(nums, list):
        raise TypeError("nums deve ser uma list")
    if not _eh_int(alvo):
        raise TypeError("alvo deve ser int")
    for x in nums:
        if not _eh_int(x):
            raise TypeError("todos os elementos de nums devem ser int")

    vistos: dict[int, int] = {}
    total = 0
    for x in nums:
        total += vistos.get(alvo - x, 0)
        vistos[x] = vistos.get(x, 0) + 1
    return total
