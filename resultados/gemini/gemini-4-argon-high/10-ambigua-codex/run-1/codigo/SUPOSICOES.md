# Suposições e Políticas Adotadas

Este documento registra as decisões de projeto adotadas na implementação de `organizar_tarefas` em `organizador.py`:

1. **Critério de desempate entre tarefas de mesma prioridade**:
   - Utiliza-se ordenação estável (Timsort padrão do Python), mantendo-se a **ordem original de aparição** na lista de entrada (FIFO) para tarefas com o mesmo valor de `prioridade`.

2. **Tratamento de entradas inválidas (campos ausentes, tipos errados ou prioridades fora da faixa)**:
   - Caso a coleção recebida não seja uma `list`, a função retorna `[]`.
   - Elementos que não sejam `dict` ou que não atendam simultaneamente aos requisitos de domínio são **ignorados (filtrados)** sem interromper o processamento das demais tarefas válidas:
     - `titulo`: deve existir, ser do tipo `str` e não ser vazio (`len(titulo) > 0`), sem aplicar normalizações (como `strip()`).
     - `prioridade`: deve existir, ser do tipo `int` (excluindo `bool`, que é subclasse de `int` em Python) e estar no intervalo fechado `0 <= prioridade <= 5`.
     - `concluida`: deve existir e ser estritamente o booleano `False` (`concluida is False`).

3. **Preservação de dados e cópia rasa**:
   - A lista original e os dicionários de entrada nunca são mutados.
   - Cada ocorrência pendente válida gera uma nova instância de `dict` via cópia rasa (`dict.copy()`), mesmo quando a mesma referência de dicionário aparece múltiplas vezes na entrada.
   - Campos extras (além de `titulo`, `prioridade` e `concluida`) e as referências/identidades de seus objetos internos são integralmente preservados.
