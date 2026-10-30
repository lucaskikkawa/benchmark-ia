# Suposições e políticas adotadas

- **Desempate:** tarefas com a mesma prioridade mantêm a ordem relativa em que
  aparecem na entrada (ordenação estável do Python; `reverse=True` preserva a
  estabilidade).
- **Repetições:** cada ocorrência pendente gera seu próprio dicionário de saída,
  mesmo que o mesmo objeto apareça várias vezes na entrada.
- **Cópia:** cada tarefa incluída é copiada de forma rasa (`dict(t)`); campos
  extras são preservados e objetos internos (ex.: listas em `etiquetas`)
  mantêm a mesma identidade. Entrada e dicionários originais não são alterados.
- **Títulos:** não são normalizados (sem `strip`, mudança de caixa etc.).
- **Entradas inválidas são ignoradas silenciosamente** (não geram exceção).
  É inválida a entrada que:
  - não é `dict`;
  - não tem `titulo` do tipo `str` não vazio;
  - não tem `prioridade` do tipo `int` (exatamente; `bool` e `float` são
    rejeitados) dentro da faixa 0 a 5, inclusive;
  - não tem `concluida` do tipo `bool` (valores "truthy"/"falsy" como `0`, `1`
    ou `"não"` são rejeitados).
- **Entrada vazia ou `None`:** retorna `[]`.
- **Desempenho:** O(n log n), adequado para dezenas de milhares de ocorrências.
