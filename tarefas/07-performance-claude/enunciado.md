# Tarefa: contar subarrays com soma exata (com desempenho)

Crie `solucao.py` no diretório de trabalho com a função:

```python
def contar_subarrays_soma(nums: list[int], k: int) -> int:
    ...
```

Retorna quantos **subarrays contíguos não vazios** de `nums` têm soma exatamente igual a `k`.
Os subarrays são contados por posição (dois trechos iguais em posições diferentes contam duas vezes).

- `nums` pode conter inteiros negativos, zeros e positivos; pode ser vazia (resultado `0`).
- `k` é um inteiro qualquer (inclusive `0` ou negativo).
- A função não deve modificar `nums`.

Exemplos:

```python
contar_subarrays_soma([1, 1, 1], 2)        # 2  -> [1,1] nas posições 0-1 e 1-2
contar_subarrays_soma([1, 2, 3], 3)        # 2  -> [1,2] e [3]
contar_subarrays_soma([1, -1, 0], 0)       # 3  -> [1,-1], [0], [1,-1,0]
contar_subarrays_soma([], 0)               # 0
```

**Desempenho:** será testada com `len(nums)` até `300_000` e precisa terminar em **menos de 2 segundos**
(uma solução O(n²) não passa). Use apenas a biblioteca padrão (Python 3.11).
