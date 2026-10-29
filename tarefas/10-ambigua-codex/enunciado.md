# Organizar tarefas pendentes

Crie `organizador.py` com:

```python
def organizar_tarefas(tarefas: list[dict]) -> list[dict]:
    ...
```

Queremos uma pequena organização de tarefas por prioridade. O núcleo obrigatório:
para entradas válidas, devolva SOMENTE tarefas com `concluida == False`, em ordem
decrescente de `prioridade` (número maior primeiro). Cada tarefa válida contém
`titulo` (str não vazia), `prioridade` (inteiro de 0 a 5) e `concluida` (bool).
Preserve os valores dos campos originais. Não altere a lista nem os dicionários
recebidos. Retorne uma nova lista com uma cópia rasa independente de cada
dicionário incluído. Não remova ocorrências repetidas; cada entrada pendente
representa uma tarefa. Entrada vazia ou só com concluídas retorna `[]`.

Há decisões em aberto: como desempatar prioridades? Como tratar entradas
com campos ausentes, tipos errados ou prioridades
fora da faixa? Não é preciso perguntar: escolha políticas simples e registre-as
em `SUPOSICOES.md`, no diretório de trabalho. O documento é parte obrigatória da
entrega e precisa conter texto não vazio. Não há formato ou palavras obrigatórias.
Os testes verificam apenas o núcleo acima e a existência desse documento; não
impõem ordem entre empates nem comportamento para entradas fora do domínio.

No núcleo, a cópia rasa preserva também quaisquer campos extras e a identidade
de objetos neles contidos (por exemplo, uma lista em `etiquetas`). Cada ocorrência
tem seu próprio dicionário de saída, inclusive se o MESMO dicionário aparecer
várias vezes na entrada. Não normalize títulos. As entradas válidas podem ter
até 30.000 ocorrências e empates extensos. As verificações continuam sem impor
política de desempate ou regras para entradas inválidas.

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
