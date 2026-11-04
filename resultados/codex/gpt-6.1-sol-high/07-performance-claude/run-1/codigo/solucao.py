def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    """Conta trechos com soma k e comprimento dentro dos limites inclusivos.

    Usa inteiros Python sem restringir sua magnitude e não altera nums.
    Complexidade esperada: O(n) em tempo e O(n) em espaço, considerando
    operações aritméticas e de dicionário de custo constante.
    """
    if comprimento_min < 1:
        raise ValueError("comprimento_min deve ser >= 1")
    if comprimento_max is not None and comprimento_max < 1:
        raise ValueError("comprimento_max deve ser >= 1")

    n = len(nums)
    limite = n if comprimento_max is None else min(comprimento_max, n)
    if comprimento_min > limite:
        return 0

    # prefixos[j] - prefixos[i] é a soma do trecho nums[i:j].
    prefixos = [0]
    soma = 0
    for numero in nums:
        soma += numero
        prefixos.append(soma)

    frequencias: dict[int, int] = {}
    obter = frequencias.get
    total = 0

    if limite == n:
        # Sem expiração de inícios, evitamos a remoção em cada iteração.
        for fim in range(comprimento_min, n + 1):
            entrada = prefixos[fim - comprimento_min]
            frequencias[entrada] = obter(entrada, 0) + 1
            total += obter(prefixos[fim] - k, 0)
    else:
        for fim in range(comprimento_min, n + 1):
            entrada = prefixos[fim - comprimento_min]
            frequencias[entrada] = obter(entrada, 0) + 1

            if fim > limite:
                saida = prefixos[fim - limite - 1]
                quantidade = frequencias[saida] - 1
                if quantidade:
                    frequencias[saida] = quantidade
                else:
                    del frequencias[saida]

            # Aqui os inícios elegíveis são exatamente os índices de
            # max(0, fim - limite) até fim - comprimento_min, inclusive.
            total += obter(prefixos[fim] - k, 0)

    return total
