# Suposições e Políticas Adotadas

Este documento registra as decisões de projeto adotadas em `organizador.py` para os pontos em aberto do enunciado.

## 1. Desempate entre prioridades iguais
- **Política:** ordenação estável — tarefas com a mesma `prioridade` mantêm exatamente a mesma ordem relativa em que aparecem na lista de entrada `tarefas`.
- **Implementação:** agrupamento em buckets de prioridade (`0` a `5`) percorridos do maior (`5`) ao menor (`0`), o que preserva a ordem de inserção em tempo linear `O(n)`.

## 2. Validação de entradas inválidas
Em vez de ignorar silenciosamente registros malformados, optou-se por falhar explicitamente com exceções padrão do Python:
- **Container de entrada:** se `tarefas` não for uma `list`, é lançado `TypeError`.
- **Tipo do item:** se algum elemento de `tarefas` não for `dict`, é lançado `TypeError`.
- **Campos ausentes:** se faltar qualquer um dos campos obrigatórios (`titulo`, `prioridade`, `concluida`), é lançado `ValueError`.
- **Tipos dos campos:**
  - `titulo` deve ser `str` (caso contrário, `TypeError`) e não vazio (`len(titulo) > 0`; strings vazias lançam `ValueError`). Strings contendo apenas espaços são aceitas sem normalização, respeitando a regra de não alterar títulos.
  - `prioridade` deve ser `int` e não `bool` (em Python `bool` é subclasse de `int`, então `True`/`False` são rejeitados com `TypeError`).
  - `concluida` deve ser `bool` (caso contrário, `TypeError`).
- **Faixa de prioridade:** `prioridade` fora do intervalo fechado `[0, 5]` lança `ValueError`.

## 3. Cópias e preservação de dados
- Cada tarefa pendente (`concluida == False`) gera um novo `dict` via `dict.copy()` (cópia rasa).
- Campos extras e referências a objetos internos (como listas em `etiquetas`) são preservados por identidade.
- Ocorrências repetidas — inclusive múltiplas referências ao mesmo objeto `dict` na entrada — produzem dicionários distintos na saída, sem deduplicação.
