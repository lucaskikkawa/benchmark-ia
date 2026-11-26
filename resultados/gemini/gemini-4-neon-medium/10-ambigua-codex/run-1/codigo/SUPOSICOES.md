# Suposições e Políticas Adotadas

Este documento registra as decisões tomadas para os pontos deixados em aberto em `enunciado.md` na implementação de `organizar_tarefas` em `organizador.py`.

## 1. Critério de desempate entre tarefas com mesma prioridade
- **Política:** ordenação estável — tarefas pendentes com a mesma `prioridade` preservam a ordem relativa em que aparecem na lista de entrada.
- **Motivação:** comportamento determinístico, previsível e executável em tempo linear $O(n)$ (via agrupamento por faixa fixa de prioridade `0..5`), atendendo com folga entradas de até 30.000 tarefas e empates extensos.

## 2. Tratamento de entradas fora do domínio (inválidas)
Adotou-se validação estrita com falha explícita (*fail-fast*) para toda a lista de entrada, inclusive para itens marcados com `concluida=True`, de modo a não mascarar dados corrompidos:

- **Tipo da entrada principal:** se `tarefas` não for uma `list`, lança `TypeError`.
- **Tipo de cada item:** se qualquer elemento de `tarefas` não for um `dict`, lança `TypeError`.
- **Campos obrigatórios ausentes:** se faltar qualquer uma das chaves `"titulo"`, `"prioridade"` ou `"concluida"`, lança `ValueError`.
- **Campo `titulo`:**
  - Se não for `str`, lança `TypeError`.
  - Se for string vazia (`""`), lança `ValueError`.
  - Strings contendo apenas espaços não são normalizadas nem rejeitadas (respeitando a regra de não normalizar títulos e validar apenas `str` não vazia).
- **Campo `prioridade`:**
  - Se não for `int` ou se for `bool` (já que `bool` é subclasse de `int` em Python), lança `TypeError`.
  - Se estiver fora do intervalo fechado `[0, 5]`, lança `ValueError`.
- **Campo `concluida`:**
  - Se não for `bool` (por exemplo, `0`, `1`, `None` ou `"False"`), lança `TypeError`.

## 3. Preservação de dados e cópia rasa
- A lista original e os dicionários recebidos nunca são modificados.
- Cada ocorrência pendente incluída na saída recebe um novo `dict` construído via cópia rasa (`dict(tarefa)`), preservando:
  - todos os campos extras presentes no dicionário original;
  - a identidade (`is`) de objetos mutáveis ou imutáveis armazenados nos valores (por exemplo, listas em `etiquetas`);
  - dicionários de saída distintos mesmo quando o mesmo objeto `dict` aparece repetido várias vezes na lista de entrada.
- Ocorrências duplicadas de tarefas pendentes são mantidas integralmente.
