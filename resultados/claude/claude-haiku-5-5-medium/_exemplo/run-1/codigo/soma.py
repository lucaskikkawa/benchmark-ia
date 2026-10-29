def soma_pares(nums: list[int]) -> int:
    """Retorna a soma dos números pares da lista (lista vazia retorna 0)."""
    return sum(n for n in nums if n % 2 == 0)
