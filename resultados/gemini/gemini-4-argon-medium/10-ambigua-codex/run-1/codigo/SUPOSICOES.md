# Suposições e Decisões de Projeto

1. **Critério de desempate de prioridades:**
   - Quando duas ou mais tarefas pendentes possuem a mesma `prioridade`, preserva-se a ordem relativa original em que apareceram na lista de entrada (ordenação estável via Timsort do Python).

2. **Tratamento de entradas inválidas (fora do domínio):**
   - Caso a coleção recebida não seja uma `list` ou algum de seus elementos não seja um `dict`, é lançada uma exceção `TypeError`.
   - Caso falte algum dos campos obrigatórios (`titulo`, `prioridade`, `concluida`), ou seus valores violem o domínio esperado (`titulo` não for `str` ou for `""`, `prioridade` não for `int` — excluindo `bool` — ou estiver fora do intervalo `0..5`, `concluida` não for `bool`), é lançada uma exceção `ValueError`.

3. **Preservação de dados e cópia rasa:**
   - Os títulos e demais campos (incluindo campos extras) são mantidos exatamente como recebidos, sem normalização.
   - Cada ocorrência pendente gera uma nova cópia rasa (`dict.copy()`), garantindo independência entre os dicionários de saída (mesmo para referências repetidas na entrada) e preservando a identidade dos objetos internos (como listas em campos extras).
