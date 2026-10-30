# Suposições

Políticas escolhidas para o que o enunciado deixa em aberto.

## Desempate

Tarefas com a mesma `prioridade` mantêm a ordem relativa em que aparecem na entrada. A ordenação é estável.

## Entradas fora do domínio

Itens que não são uma tarefa válida são ignorados. O restante da lista continua sendo processado. Não há exceção nem normalização.

Uma tarefa é válida quando é um `dict` com:

- `titulo`: `str` não vazia, exatamente como recebida (espaços não são removidos nem o texto é alterado);
- `prioridade`: `int` builtin de 0 a 5, inclusive. `bool` não conta como inteiro;
- `concluida`: `bool` builtin.

Só entram no resultado as válidas com `concluida` igual a `False`. Campos extras são copiados sem mudança. Cada ocorrência pendente gera um dicionário novo (`dict(tarefa)`), mesmo que o mesmo objeto apareça mais de uma vez na entrada. A cópia é rasa: objetos aninhados, como uma lista em `etiquetas`, permanecem os mesmos objetos.

A função não altera a lista recebida nem os dicionários originais. Entrada vazia, só com concluídas ou só com itens inválidos devolve `[]`.
