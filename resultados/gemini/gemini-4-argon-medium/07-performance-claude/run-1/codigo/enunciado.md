# Tarefa: contar subarrays com soma exata e comprimento limitado (com desempenho)

Crie `solucao.py` no diretório de trabalho com a função:

```python
def contar_subarrays_soma(
    nums: list[int],
    k: int,
    comprimento_min: int = 1,
    comprimento_max: int | None = None,
) -> int:
    ...
```

Retorna quantos **subarrays contíguos não vazios** de `nums` têm soma exatamente igual a `k` **e**
comprimento (número de elementos) entre `comprimento_min` e `comprimento_max`, inclusive
(`comprimento_max=None` = sem limite superior). Os subarrays são contados por posição (dois trechos
iguais em posições diferentes contam duas vezes).

- `nums` pode conter inteiros negativos, zeros e positivos, de qualquer magnitude (inclusive maiores
  que 2**63); pode ser vazia (resultado `0`).
- `k` é um inteiro qualquer (inclusive `0` ou negativo).
- `comprimento_min` deve ser `>= 1` e `comprimento_max`, se informado, `>= 1`; caso contrário,
  `ValueError`. Se `comprimento_min > comprimento_max` (ou `comprimento_min > len(nums)`), o resultado é `0`.
- A função não deve modificar `nums`.

Exemplos:

```python
contar_subarrays_soma([1, 1, 1], 2)                       # 2  -> [1,1] nas posições 0-1 e 1-2
contar_subarrays_soma([1, 2, 3], 3)                       # 2  -> [1,2] e [3]
contar_subarrays_soma([1, -1, 0], 0)                      # 3  -> [1,-1], [0], [1,-1,0]
contar_subarrays_soma([], 0)                              # 0
contar_subarrays_soma([1, -1, 0], 0, comprimento_min=2)   # 2  -> [1,-1], [1,-1,0]
contar_subarrays_soma([1, -1, 0], 0, comprimento_max=2)   # 2  -> [1,-1], [0]
contar_subarrays_soma([0, 0, 0], 0, 2, 2)                 # 2
```

**Desempenho:** será testada com `len(nums)` até `300_000` (com e sem limites de comprimento, inclusive
`comprimento_max` na casa dos milhares) e cada chamada precisa terminar em **menos de 2 segundos**.
Soluções O(n²) ou O(n · comprimento_max) não passam. Use apenas a biblioteca padrão (Python 3.11).
