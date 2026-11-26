# Suposições de Implementação

Este documento registra as decisões adotadas para os pontos em aberto de `organizador.py`.

## 1. Política de desempate

- Quando duas ou mais tarefas pendentes possuem a mesma `prioridade`, a ordenação é **estável**: preserva-se a ordem relativa original em que as tarefas aparecem na lista de entrada.

## 2. Tratamento de entradas inválidas (política *fail-fast*)

Todas as entradas são validadas antes/durante o processamento (inclusive tarefas com `concluida == True`), lançando exceções explícitas em vez de ignorar silenciosamente registros malformados:

- **Tipo da entrada principal**: se `tarefas` não for uma instância de `list`, é lançada `TypeError`.
- **Tipo de cada item**: se algum elemento de `tarefas` não for `dict`, é lançada `TypeError`.
- **Campos ausentes**: se faltar qualquer uma das chaves obrigatórias (`"titulo"`, `"prioridade"`, `"concluida"`), é lançada `ValueError`.
- **`titulo`**: deve ser `str` (caso contrário, `TypeError`) e não vazio (`titulo != ""`, caso contrário, `ValueError`). Não é feita normalização nem remoção de espaços.
- **`prioridade`**: deve ser `int` estrito, rejeitando `bool` e outros tipos (`TypeError`), e estar no intervalo fechado `[0, 5]` (caso contrário, `ValueError`).
- **`concluida`**: deve ser `bool` (`TypeError` para outros tipos, como `int` ou `str`).

## 3. Preservação de dados, duplicatas e desempenho

- Cada tarefa incluída na saída é produzida via cópia rasa (`dict.copy()`), preservando valores originais, campos extras e a identidade de objetos internos (como listas).
- Ocorrências repetidas (inclusive referências ao mesmo objeto `dict`) são mantidas integralmente, gerando um novo `dict` independente por ocorrência pendente.
- A ordenação usa baldes para as prioridades `0` a `5`, executando em tempo linear `O(n)` para lidar com até 30.000 ocorrências e empates extensos com folga.
