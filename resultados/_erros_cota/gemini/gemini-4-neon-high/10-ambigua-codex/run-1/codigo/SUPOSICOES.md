# Suposições e Políticas Adotadas

Este documento registra as decisões de projeto escolhidas para os pontos em aberto da especificação de `organizar_tarefas` em `organizador.py`.

## 1. Desempate entre prioridades iguais

- **Política:** ordenação estável preservando a ordem relativa original da lista de entrada.
- **Motivo:** o algoritmo Timsort nativo do Python (`list.sort(..., reverse=True)`) garante estabilidade em $O(n \log n)$, oferece comportamento determinístico e eficiente mesmo para entradas grandes (30.000+ tarefas com muitos empates) e não exige normalização ou comparação de títulos.

## 2. Tratamento de entradas inválidas

- **Política:** validação estrita (*fail-fast*) aplicada a toda a entrada, inclusive às tarefas marcadas como `concluida == True`, lançando exceções explícitas sem tentar corrigir ou descartar silenciosamente itens fora do domínio.
- **Regras de exceção:**
  - `TypeError` quando `tarefas` não for uma `list`.
  - `TypeError` quando algum elemento de `tarefas` não for um `dict`.
  - `ValueError` quando algum elemento não contiver qualquer um dos campos obrigatórios (`titulo`, `prioridade`, `concluida`).
  - `TypeError` quando `titulo` não for `str`, e `ValueError` quando `titulo` for a string vazia (`""`).
  - `TypeError` quando `prioridade` não for `int` ou for `bool` (booleanos são explicitamente rejeitados, embora `bool` seja subclasse de `int` em Python).
  - `ValueError` quando `prioridade` estiver fora do intervalo fechado `0..5`.
  - `TypeError` quando `concluida` não for `bool` (valores *truthy*/*falsy* como `0`, `1` ou `None` são rejeitados).

## 3. Títulos, campos extras, duplicatas e imutabilidade

- **Títulos:** não passam por normalização (espaços, caixa e acentuação são preservados exatamente como recebidos); qualquer `str` com comprimento maior que zero é aceita.
- **Cópia rasa e identidade:** cada tarefa incluída na saída é gerada via `dict.copy()`, preservando todos os campos extras e mantendo a identidade (`is`) de objetos mutáveis internos (como listas em `etiquetas`).
- **Ocorrências repetidas:** não há remoção de duplicatas. Mesmo quando o mesmo objeto `dict` aparece múltiplas vezes na lista de entrada, cada ocorrência gera um dicionário de saída independente.
- **Imutabilidade da entrada:** nem a lista `tarefas` nem os dicionários contidos nela são modificados.
- **Casos vazios:** lista vazia ou contendo apenas tarefas concluídas retorna uma nova lista vazia (`[]`).
