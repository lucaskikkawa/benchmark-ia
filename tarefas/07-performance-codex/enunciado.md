# Contar pares sem enumerá-los

Crie `pares.py` com:

```python
def contar_pares(valores, alvo: int) -> int:
    ...
```

Conte pares de índices distintos `(i, j)` com `i < j` e
`valores[i] + valores[j] == alvo`. `valores` é um iterável finito de inteiros;
`alvo` é inteiro. Duplicatas representam elementos distintos: `[2, 2, 2]`, alvo 4,
produz 3 pares. Não conte um elemento consigo mesmo nem conte o mesmo par duas
vezes. Vazio e um elemento produzem zero. Não modifique listas recebidas e aceite
geradores de uma passagem. Nenhuma validação de outros tipos é exigida.

Use tempo esperado O(n) e memória O(k), k = quantidade de valores distintos.
Os testes geram entradas de até 200.000 elementos e exigem que cada chamada
nessas entradas termine em menos de 2 segundos (medição com `perf_counter`, sem
incluir geração/importação). Um processo auxiliar é encerrado após 5 segundos
para evitar travamento de soluções quadráticas. Não use acesso à rede, cache
persistente ou dependências. Exemplo: `[1, 3, 2, 2]`, alvo 4, retorna 2.

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
