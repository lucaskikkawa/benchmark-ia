def soma_pares(nums: list[int]) -> int:
    return sum(n for n in nums if n % 2 == 0)
