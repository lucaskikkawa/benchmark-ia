def soma_pares(nums: list[int]) -> int:
    """Retorna a soma dos números pares em nums."""
    return sum(numero for numero in nums if numero % 2 == 0)
