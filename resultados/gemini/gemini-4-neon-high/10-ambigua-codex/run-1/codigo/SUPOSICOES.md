# Suposições e Políticas Adotadas

Este documento registra as decisões de projeto adotadas na implementação de `organizar_tarefas` em `organizador.py` para os pontos deixados em aberto no enunciado.

## 1. Critério de desempate entre prioridades iguais
- **Política:** ordenação estável — tarefas pendentes com a mesma `prioridade` mantêm exatamente a ordem relativa em que aparecem na lista de entrada.
- **Justificativa:** é simples, previsível, determinística e evita depender de normalização ou comparação de títulos (além de permitir organização em tempo linear `O(n)` por faixas de prioridade `0..5`, atendendo com folga entradas de até 30.000 tarefas e empates extensos).

## 2. Tratamento de entradas inválidas
Adotou-se uma política estrita (*fail-fast*), validando toda a lista de entrada (inclusive tarefas com `concluida == True`) e lançando exceções explícitas em vez de ignorar ou corrigir silenciosamente dados fora do domínio:

- **Tipo da entrada principal (`tarefas`):** exige-se `list`; caso contrário, lança `TypeError`.
- **Tipo de cada item:** cada elemento de `tarefas` deve ser um `dict`; caso contrário, lança `TypeError`.
- **Campos ausentes:** se qualquer um dos campos obrigatórios (`titulo`, `prioridade`, `concluida`) estiver ausente, lança `ValueError`.
- **Validação de `titulo`:** deve ser `str` (caso contrário, `TypeError`) e ter comprimento maior que zero (`len(titulo) > 0`; caso contrário, `ValueError`). Títulos não são normalizados nem têm espaços removidos (strings compostas apenas por espaços são aceitas por não serem vazias).
- **Validação de `prioridade`:** deve ser `int` e não `bool` (em Python `bool` é subclasse de `int`; valores booleanos lançam `TypeError`). Deve estar no intervalo fechado `0 <= prioridade <= 5`; valores fora dessa faixa lançam `ValueError`.
- **Validação de `concluida`:** deve ser estritamente `bool` (`True` ou `False`); outros tipos (como `0`, `1` ou `None`) lançam `TypeError`.

## 3. Campos extras, duplicatas e cópia rasa
- **Campos extras:** são permitidos e preservados sem modificação.
- **Cópia rasa independente:** cada tarefa pendente incluída na saída é criada com `dict(tarefa)`, garantindo que:
  - nem a lista de entrada nem os dicionários originais sejam modificados;
  - cada ocorrência na saída possua sua própria instância de `dict` (inclusive quando o mesmo objeto `dict` aparece repetido várias vezes na entrada);
  - a identidade dos objetos armazenados nos valores (como listas em campos extras) seja preservada.
- **Duplicatas:** ocorrências repetidas de tarefas pendentes não são removidas.
