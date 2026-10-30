# Suposições e Decisões de Implementação

Este documento descreve as decisões adotadas na implementação da função `organizar_tarefas` no módulo `organizador.py`.

---

## 1. Política de Desempate de Prioridades

- **Regra**: Em caso de tarefas com o mesmo nível de prioridade, a ordem original de inserção (estabilidade / FIFO) é preservada.
- **Justificativa**: A ordenação utiliza o algoritmo nativo Timsort do Python (`list.sort(key=..., reverse=True)`), que garante estabilidade. Isso preserva a cronologia relativa das tarefas conforme foram fornecidas na entrada.

---

## 2. Tratamento de Entradas Inválidas e Casos Fora do Domínio

Uma tarefa é considerada válida quando atende aos seguintes critérios:
1. É uma instância de dicionário (`isinstance(t, dict)`).
2. Contém o campo `'titulo'`, cujo valor é uma `str` não vazia (`len(titulo) > 0`). Não há normalização ou remoção de espaços em branco adicionais.
3. Contém o campo `'prioridade'`, cujo tipo é estritamente `int` (`type(prioridade) is int`, evitando que booleanos `True`/`False` sejam tratados como inteiros) e cujo valor está no intervalo fechado de `0` a `5` (`0 <= prioridade <= 5`).
4. Contém o campo `'concluida'`, cujo tipo é estritamente `bool` (`type(concluida) is bool`).

### Políticas Adotadas:
- **Campos ausentes, tipos incorretos ou valores fora da faixa**: Entradas inválidas são silenciosamente ignoradas/descartadas, não sendo incluídas na lista final e sem interrupção do processamento.
- **Entrada principal inválida**: Caso o argumento `tarefas` seja `None`, não seja um iterável ou seja de tipos como `str`, `bytes` ou `dict`, a função retorna com segurança uma lista vazia `[]`.

---

## 3. Preservação de Campos e Cópia Rasa

- **Cópia Rasa Independente**: Cada ocorrência de tarefa pendente incluída na lista de saída recebe uma nova cópia rasa (`tarefa.copy()`). Isso garante que:
  - A lista e os dicionários originais recebidos na entrada não sofrem nenhuma mutação.
  - Ocorrências repetidas do mesmo objeto de dicionário na entrada geram instâncias independentes de dicionário na saída (`res[i] is not res[j]`).
  - Campos extras (como listas, dicionários aninhados em `etiquetas`, metadados, etc.) são preservados mantendo suas referências internas originais.

---

## 4. Ocorrências Repetidas e Tarefas Concluídas

- **Repetições**: Tarefas duplicadas/repetidas não são desduplicadas; cada entrada pendente representa uma tarefa individual e é mantida na saída.
- **Concluídas**: Tarefas onde `concluida is True` são filtradas e omitidas do resultado. Se todas estiverem concluídas ou a lista estiver vazia, o retorno é `[]`.
