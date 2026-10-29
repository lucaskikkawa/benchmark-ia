"""Contagem de pares i < j cuja soma é o alvo."""

from collections import Counter


def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Conta pares de índices i < j com nums[i] + nums[j] == alvo.

    Valores iguais usam a combinação C(freq, 2). Não altera a lista.
    bool não é aceito como int.
    """
    _validar(nums, alvo)
    frequencia = Counter(nums)
    total = 0
    for valor, vezes in frequencia.items():
        complemento = alvo - valor
        if valor < complemento:
            total += vezes * frequencia[complemento]
        elif valor == complemento:
            total += vezes * (vezes - 1) // 2
    return total


def _validar(nums: list[int], alvo: int) -> None:
    if not isinstance(nums, list):
        raise TypeError("nums deve ser list")
    if isinstance(alvo, bool) or not isinstance(alvo, int):
        raise TypeError("alvo deve ser int")
    for valor in nums:
        if isinstance(valor, bool) or not isinstance(valor, int):
            raise TypeError("nums deve conter apenas int")
