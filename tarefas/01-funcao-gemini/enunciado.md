# 01 - Resumidor de Intervalos Numéricos

Implemente a função `resumir_intervalos` no arquivo `solucao.py` na raiz do seu diretório de trabalho.

## Especificação

A função deve ter a seguinte assinatura:

```python
def resumir_intervalos(numeros: list[int]) -> str:
    ...
```

### Comportamento:
1. Recebe uma lista de inteiros (`numeros`). A lista pode conter valores desordenados, duplicados ou negativos.
2. Deve remover números duplicados e ordenar os valores em ordem crescente.
3. Deve agrupar sequências de números consecutivos em intervalos no formato `"inicio-fim"` se houver 2 ou mais números consecutivos (por exemplo, `[1, 2, 3]` vira `"1-3"`; `[7, 8]` vira `"7-8"`).
4. Números que não formam sequência com seus vizinhos devem aparecer isolados (por exemplo, `5` vira `"5"`).
5. Os intervalos e números isolados devem ser concatenados em uma única string separados por vírgula e espaço (`", "`).
6. Se a lista de entrada for vazia, deve retornar uma string vazia `""`.
7. **Validação de tipos**:
   - Caso o argumento `numeros` não seja uma lista (`isinstance(numeros, list)` deve ser verdadeiro), levanta `TypeError`.
   - Todos os elementos devem ser estritamente do tipo inteiro primitivo (`type(x) is int`). Note que `bool` e quaisquer subclasses de `int` não são permitidos e devem levantar `TypeError`.
8. **Imutabilidade**: A função não deve modificar a lista original recebida no parâmetro `numeros` (não realize mutações in-place na lista do chamador).
9. A função deve suportar listas com grandes volumes de dados de forma eficiente, bem como inteiros de magnitude arbitrária (positivos ou negativos).

### Exemplos:
- `resumir_intervalos([1, 2, 3, 5, 7, 8, 9])` -> `"1-3, 5, 7-9"`
- `resumir_intervalos([9, 1, 8, 2, 7, 3, 5])` -> `"1-3, 5, 7-9"`
- `resumir_intervalos([1, 1, 2, 2, 3])` -> `"1-3"`
- `resumir_intervalos([42])` -> `"42"`
- `resumir_intervalos([])` -> `""`
- `resumir_intervalos([-3, -2, -1, 1, 2])` -> `"-3--1, 1-2"`
