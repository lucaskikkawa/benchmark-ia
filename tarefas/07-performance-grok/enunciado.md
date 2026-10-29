# Tarefa: contar pares que somam um alvo

Crie `solucao.py` no diretório de trabalho com a função abaixo. Só a biblioteca padrão. Não crie outros arquivos.

```python
def pares_com_soma(nums: list[int], alvo: int) -> int:
    """Quantidade de pares i < j com nums[i] + nums[j] == alvo."""
```

## Regras

- Conte pares de **índices** `i < j`, não pares de valores únicos. `[1, 1, 1]` e alvo `2` valem `3`.
- Quando `2 * x == alvo`, a resposta daquele valor é `C(freq, 2) = freq * (freq - 1) // 2`.
- Números negativos e zero são válidos.
- Lista vazia ou com um elemento devolve `0`.
- Não altere `nums`.
- `nums` tem de ser `list`. Cada elemento e `alvo` têm de ser `int`. `bool` não conta como `int` (`TypeError`). Outro tipo → `TypeError`.
- A resposta cabe num `int` do Python. Não materialize a lista de pares: com dezenas de milhares de valores iguais a resposta passa de 10^9.
- Há teste com `n = 100_000`. Um laço duplo não termina no limite de 2 segundos. Uma passagem com contagem de frequências (ou dois ponteiros depois de ordenar **uma cópia**) passa.

## Exemplos

```python
pares_com_soma([], 0)            # 0
pares_com_soma([5], 10)          # 0
pares_com_soma([1, 2, 3], 4)     # 1  (1+3)
pares_com_soma([1, 3, 1, 3], 4)  # 4
pares_com_soma([2, 2, 2], 4)     # 3
pares_com_soma([0, 0, 0, 0], 0)  # 6
pares_com_soma([-2, 0, 2, -2], 0)  # 2
```
