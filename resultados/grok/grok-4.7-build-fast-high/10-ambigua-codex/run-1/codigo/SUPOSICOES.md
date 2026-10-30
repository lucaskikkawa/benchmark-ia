# Suposições

Políticas escolhidas para o que o enunciado deixa em aberto. O núcleo
(pendentes válidas, prioridade decrescente, cópia rasa, sem mutar a entrada,
sem remover repetidas) não depende destas escolhas para ser verificado.

## Desempate

Prioridades iguais conservam a ordem relativa da entrada. A implementação
agrupa as tarefas em seis baldes, um por prioridade de 0 a 5, e emite do
balde 5 até o balde 0. Isso é estável e linear no número de ocorrências,
adequado a até 30.000 itens com muitos empates.

## Entradas fora do domínio

Qualquer item que não satisfaça todas as condições abaixo é ignorado e não
entra no resultado:

- o item é um `dict`;
- `titulo` é `str` e não é a string vazia (`""`); espaços e outros caracteres
  são mantidos como estão, sem `strip` nem outra normalização;
- `prioridade` é `int` na faixa inclusiva de 0 a 5; `bool` não conta como
  inteiro (`True`/`False` são rejeitados);
- `concluida` é exatamente `bool`.

`concluida is True` também fica de fora, por já estar concluída. Campos
ausentes, tipos errados, prioridade fora de 0..5 e itens que não são
dicionários seguem a mesma regra: são descartados. Os demais campos de uma
tarefa aceita são copiados sem alteração.

Uma entrada vazia, `None` ou uma sequência só com concluídas ou inválidas
devolve `[]`.

## Cópia

Cada ocorrência aceita gera um `dict` novo (`dict(tarefa)`), mesmo quando o
mesmo dicionário aparece mais de uma vez na entrada. A cópia é rasa: objetos
aninhados, como uma lista em `etiquetas`, permanecem os mesmos objetos. A
lista recebida e os dicionários originais não são modificados.
