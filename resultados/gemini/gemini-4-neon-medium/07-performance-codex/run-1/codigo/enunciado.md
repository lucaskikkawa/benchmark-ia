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
Os testes geram entradas de até 1.000.000 de elementos e exigem que cada chamada
nessas entradas termine em menos de 5 segundos (medição com `perf_counter`, sem
incluir geração/importação). Um processo auxiliar é encerrado após 12 segundos
para evitar travamento de soluções quadráticas. Não use acesso à rede, cache
persistente ou dependências. Exemplo: `[1, 3, 2, 2]`, alvo 4, retorna 2.

Inteiros podem exceder 64 bits e devem ser comparados com exatidão.
A memória O(k) também vale para geradores: não materialize toda a entrada.
Além da medição de tempo em subprocesso, há uma medição separada com
`tracemalloc` para um gerador de 1.000.000 de valores, com no máximo quatro
valores distintos: o pico adicional deve ser menor que 4 MiB. A medição de
memória não está sujeita ao limite de 5 segundos da medição de tempo; seu
processo tem limite externo folgado de 30 segundos. Não retenha estado entre
chamadas.

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
