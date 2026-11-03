# Suposições

Políticas escolhidas para o que o enunciado deixa em aberto. O núcleo
(pendentes com `concluida is False`, prioridade de 5 a 0, cópia rasa,
sem mutar a entrada, sem descartar repetições) não depende destas escolhas.

## Desempate de prioridade

Quando duas tarefas pendentes têm a mesma `prioridade`, a ordem relativa
da entrada é preservada: a que apareceu primeiro continua na frente.
A ordenação é estável e usa um balde por prioridade (0 a 5), em vez de
uma comparação genérica, para continuar linear mesmo com milhares de empates.

## Entradas fora do domínio

Itens que não são uma tarefa válida são ignorados e não aparecem no
resultado. A varredura segue para o próximo item. Não há exceção, valor
sentinela nem mensagem de erro.

Uma tarefa é válida quando todas as condições abaixo se cumprem:

- o item é um `dict`;
- `titulo` existe, é `str` e não é a string vazia (`""`);
- `prioridade` existe, é exatamente `int` (não `bool`) e está entre 0 e 5, inclusive;
- `concluida` existe e é exatamente `bool`.

`True` e `False` não são aceitos como prioridade, embora `bool` seja
subclasse de `int`. Inteiros fora de 0..5, floats (inclusive `3.0`),
strings numéricas e `None` também são rejeitados.

Título não é normalizado: espaços nas pontas, maiúsculas e caracteres
internos permanecem como vieram. Uma string só com espaços é não vazia
e, portanto, válida.

Tarefa válida com `concluida is True` está no domínio, mas fica de fora
do resultado porque já foi concluída. Só `False` entra na lista devolvida.
`0`, `1`, `None` e outros valores no lugar de `concluida` são inválidos
e também ficam de fora.

Campos além de `titulo`, `prioridade` e `concluida` não invalidam a tarefa.
Eles são copiados junto. Objetos aninhados (por exemplo, a lista em
`etiquetas`) mantêm a mesma identidade na cópia rasa.

O mesmo dicionário repetido na entrada gera uma cópia nova por ocorrência.
A lista recebida e os dicionários recebidos não são alterados.

Se `tarefas` não for iterável, a função propaga o `TypeError` natural do
`for`. Lista vazia devolve `[]`.
