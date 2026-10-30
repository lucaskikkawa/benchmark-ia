# Suposições e políticas adotadas

## Desempate
- Tarefas com a mesma `prioridade` mantêm a **ordem relativa da entrada**
  (ordenação estável via `sorted(..., reverse=True)`, que preserva a ordem
  original dos empates). Nenhum outro critério (título, etc.) é usado.

## Validação de entradas
A função é estrita: se **qualquer** elemento da entrada for inválido, levanta
`ValueError` com o índice da tarefa e o motivo, sem devolver resultado parcial.
Preferi falhar a descartar silenciosamente dados malformados. A validação vale
também para tarefas concluídas.

Uma tarefa é válida quando:
- é um `dict`;
- contém `titulo`, `prioridade` e `concluida`;
- `titulo` é `str` não vazia (não é normalizado: espaços/maiúsculas são mantidos;
  uma string só com espaços é aceita, pois não é vazia);
- `prioridade` é `int` de 0 a 5, inclusive. `bool` (`True`/`False`) **não** é
  aceito, embora seja subclasse de `int`; `float` (mesmo `3.0`) e strings
  numéricas também não;
- `concluida` é `bool` (não se aceitam valores "truthy" como `0`, `1`, `"sim"`).

Se `tarefas` não for uma `list`, também é levantado `ValueError`.

## Saída
- Somente tarefas com `concluida == False`.
- Nova lista; cada item é uma cópia rasa (`dict(tarefa)`) independente, inclusive
  quando o mesmo dicionário aparece várias vezes na entrada.
- Campos extras são preservados, e objetos neles contidos (ex.: lista em
  `etiquetas`) mantêm a identidade (cópia rasa, não profunda).
- Duplicatas não são removidas.
- A entrada (lista e dicionários) não é modificada.
- Complexidade O(n log n); adequada para dezenas de milhares de tarefas.
