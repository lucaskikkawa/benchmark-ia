# Unir intervalos fechados

Crie `solucao.py` no diretório de trabalho com:

```python
def unir_intervalos(intervalos, *, limites=None) -> list[tuple[int, int]]:
    ...
```

`intervalos` é um iterável finito de pares de inteiros `(inicio, fim)` com
`inicio <= fim`. Devolva a união como uma lista de tuplas, ordenada por início.
Intervalos fechados que se sobrepõem ou compartilham uma extremidade devem ser
fundidos. Intervalos separados por uma unidade NÃO se fundem: `(1, 2)` e `(3, 4)`
continuam separados. Duplicatas não alteram a união. A entrada vazia resulta em `[]`.
Se qualquer par tiver início maior que o fim, lance `ValueError`.
Não modifique listas recebidas. Aceite também geradores consumidos uma única vez.
Outros tipos ou pares malformados ficam fora do escopo.

Exemplo: `unir_intervalos([(5, 8), (1, 3), (3, 6), (10, 10)])`
retorna `[(1, 8), (10, 10)]`.

A função aceita o argumento opcional somente por nome `limites=None`. Quando informado,
`limites` é um par de inteiros `(minimo, maximo)` fechado: interseccione cada
intervalo com esses limites antes de unir, descartando intersecções vazias.
Um ponto na extremidade do recorte deve ser retido. Limites invertidos lançam
`ValueError`, inclusive com entrada vazia. Valide TODOS os pares originais,
inclusive os que ficariam fora do recorte. Não altere os limites recebidos.
Inteiros têm precisão arbitrária: não converta coordenadas para ponto flutuante.
As entradas podem ter até 100.000 intervalos; use ordenação e varredura,
com tempo O(n log n) e memória O(n).

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
