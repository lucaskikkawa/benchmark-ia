# Suposições

Políticas usadas por `organizar_tarefas` quando o enunciado deixa a decisão em aberto.

## Desempate de prioridade

A ordenação é estável. Tarefas pendentes com a mesma `prioridade` permanecem na mesma ordem relativa em que apareciam na lista de entrada. Nenhuma chave secundária (título, posição artificial ou outro campo) é usada para desempatar.

## Entradas fora do domínio

Itens que não são uma tarefa válida e pendente são omitidos. A função não lança erro por causa deles e não altera a lista recebida.

Uma tarefa entra no resultado somente quando:

- o item é um `dict`;
- `titulo` é `str` e não é a string vazia (espaços e maiúsculas são preservados; o título não é normalizado);
- `prioridade` é `int` de 0 a 5, inclusive (valores booleanos não contam como inteiro);
- `concluida` é exatamente `False`.

Ficam de fora, entre outros casos: campos ausentes, tipos errados, prioridade fora de 0–5, título vazio, tarefa já concluída (`concluida is True`) e itens que não são dicionários.

Se o argumento não for uma `list`, o resultado é `[]`.

Cada tarefa aceita gera um dicionário novo (`dict(tarefa)`), mesmo quando o mesmo objeto aparece mais de uma vez na entrada. A cópia é rasa: campos extras são mantidos e objetos aninhados (por exemplo uma lista em `etiquetas`) continuam sendo os mesmos objetos.
