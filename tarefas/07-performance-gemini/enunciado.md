# 07 - Maior Subarray com Soma Alvo (Algoritmo de Alta Performance)

Implemente a função `maior_subarray_soma` no arquivo `otimizador.py` na raiz do seu diretório de trabalho.

## Assinatura

```python
def maior_subarray_soma(numeros: list[int], alvo: int) -> int:
    ...
```

## Especificação

A função recebe:
- `numeros`: lista de inteiros (podendo conter números positivos, negativos e zeros).
- `alvo`: inteiro representando a soma desejada.

Ela deve retornar o **comprimento máximo** (quantidade de elementos) de um subarray contíguo cuja soma seja exatamente igual a `alvo`.

### Regras:
1. Se nenhum subarray contíguo somar `alvo`, ou se a lista for vazia, retorne `0`.
2. Um subarray é uma sequência contígua de elementos da lista (isto é, `numeros[i:j]`).
3. Em caso de múltiplos subarrays que somem `alvo`, deve ser retornado o comprimento do maior deles.
4. **Validação de tipos**:
   - Se `numeros` não for uma lista (`list`), levanta `TypeError`.
   - Se qualquer elemento de `numeros` não for estritamente um inteiro primitivo (`type(x) is int`, rejeitando `bool`), levanta `TypeError`.
   - Se `alvo` não for estritamente um inteiro primitivo (`type(alvo) is int`, rejeitando `bool`), levanta `TypeError`.

### Requisito de Desempenho:
- O benchmark executa testes com listas contendo **centenas de milhares de elementos** ($N \ge 350.000$).
- Cada chamada com 350.000 elementos tem limite de **5 segundos** para o cálculo, excluindo geração dos dados e inicialização do processo. Há margem para variações de máquina; soluções quadráticas $O(N^2)$ não atendem a esse limite. Execuções que não retornam são interrompidas após 15 segundos, incluindo a inicialização do processo.
- Sua solução deve operar em complexidade linear $O(N)$ de tempo e espaço.

### Exemplos:
- `maior_subarray_soma([1, -1, 5, -2, 3], 3)` -> `4` (o subarray `[1, -1, 5, -2]` soma 3 e tem tamanho 4)
- `maior_subarray_soma([-2, -1, 2, 1], 1)` -> `2` (o subarray `[-1, 2]` tem tamanho 2)
- `maior_subarray_soma([1, 2, 3], 10)` -> `0` (nenhum subarray soma 10)
- `maior_subarray_soma([], 0)` -> `0`
