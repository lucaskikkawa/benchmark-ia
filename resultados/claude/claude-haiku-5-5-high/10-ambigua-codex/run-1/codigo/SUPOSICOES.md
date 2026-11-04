# Suposições e políticas adotadas

Este documento registra as decisões tomadas para os pontos em aberto do enunciado.

## Entradas válidas

Uma entrada é válida quando é um `dict` e satisfaz todas as condições:

- `titulo` é `str` e não está vazio nem contém apenas espaços. O título é mantido exatamente como recebido, sem normalização.
- `prioridade` é `int` (exceto `bool`) entre 0 e 5, inclusive.
- `concluida` é `bool` (exatamente `True` ou `False`).

## Entradas inválidas

Entradas inválidas são descartadas silenciosamente: não geram erro e não aparecem na saída. Isso inclui:

- campos obrigatórios ausentes;
- tipos errados (por exemplo, `prioridade` como `"3"`, `3.0` ou `True`; `concluida` como `0` ou `"não"`);
- prioridades fora de 0 a 5;
- itens que não são dicionários.

Se `tarefas` for `None` ou vazia, o retorno é `[]`.

## Filtro

Apenas entradas válidas com `concluida` igual a `False` entram na saída. Entradas válidas já concluídas são omitidas.

## Ordenação e empates

- A ordenação é decrescente por `prioridade`, com maior prioridade primeiro.
- Empates de prioridade mantêm a ordem em que aparecem na entrada. A ordenação é estável.

## Duplicatas

Nenhuma deduplicação é feita. Cada ocorrência pendente gera uma saída, mesmo que seja o mesmo dicionário repetido.

## Cópia e imutabilidade

- A entrada nunca é modificada.
- Cada saída é uma cópia rasa nova do dicionário (`dict(tarefa)`). Os valores dos campos originais são preservados.
- Campos extras são copiados junto. Objetos aninhados, como a lista em `etiquetas`, mantêm a mesma identidade, conforme a especificação de cópia rasa.
- Se o mesmo dicionário aparecer várias vezes na entrada, cada ocorrência recebe seu próprio dicionário de saída.

## Desempenho

A função usa uma passagem de filtro e uma ordenação, com custo O(n log n). Isso atende ao limite de 30.000 ocorrências.
