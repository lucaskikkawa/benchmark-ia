# Suposições e Políticas de Decisão

Este documento registra as decisões tomadas para os pontos em aberto na especificação do organizador de tarefas (`organizador.py`).

## 1. Política de Desempate de Prioridades

- **Critério**: Quando duas ou mais tarefas possuem a mesma `prioridade`, preserva-se a ordem relativa original em que elas apareceram na lista de entrada (ordenação estável / FIFO relativo).
- **Motivação**: O método de ordenação padrão do Python (`Timsort`) é estável por definição, previsível, com complexidade de tempo ótima ($O(N)$ no melhor caso e $O(N \log N)$ no pior caso).

## 2. Tratamento de Entradas Inválidas e Fora do Domínio

As seguintes políticas foram adotadas para lidar com entradas fora da especificação válida:

- **Estrutura geral da entrada**: Caso o parâmetro `tarefas` não seja uma lista ou tupla (por exemplo, `None` ou outro tipo incompatível), a função retorna uma lista vazia `[]`.
- **Elementos que não são dicionários**: Qualquer item na coleção que não seja do tipo `dict` é desconsiderado e não entra na saída.
- **Campos obrigatórios ausentes**: Qualquer dicionário que não possua todos os três campos obrigatórios (`titulo`, `prioridade`, `concluida`) é ignorado.
- **Validação de `titulo`**:
  - Deve ser estritamente do tipo `str`.
  - Não pode ser vazio (`""`).
  - Títulos não são normalizados (espaços, maiúsculas/minúsculas e caracteres especiais são preservados).
  - Tarefas com títulos inválidos são descartadas.
- **Validação de `prioridade`**:
  - Deve ser do tipo `int` (valores booleanos são rejeitados, já que em Python `bool` herda de `int`).
  - Deve estar estritamente dentro da faixa `0` a `5` (inclusive).
  - Valores fora dessa faixa ou de outros tipos (ex.: `float`, `str`, `None`) são descartados.
- **Validação de `concluida`**:
  - Deve ser estritamente do tipo `bool` (`True` ou `False`).
  - Valores não-booleanos (ex.: `0`, `1`, `None`, `"false"`) são descartados.
- **Campos extras**:
  - Dicionários contendo campos adicionais além dos obrigatórios são considerados válidos, desde que cumpram os requisitos dos campos base.
  - Todos os campos adicionais são integralmente preservados na cópia rasa do dicionário retornado, incluindo referências a objetos mutáveis (como listas ou outros dicionários).
- **Ocorrências repetidas**:
  - Se o mesmo dicionário (ou dicionários idênticos) aparecer múltiplas vezes na entrada, cada ocorrência gera um novo dicionário independente na saída, preservando a contagem de tarefas.
