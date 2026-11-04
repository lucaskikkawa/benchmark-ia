# Suposições e políticas adotadas

## Núcleo
- Só entram na saída tarefas com `concluida == False`; cada ocorrência pendente gera uma entrada.
- Ordenação por `prioridade` decrescente.

## Desempate
- Prioridades iguais mantêm a ordem em que aparecem na entrada (ordenação estável). Não há critério secundário.

## Entradas inválidas
Uma entrada é considerada válida somente se for `dict` com:
- `titulo`: `str` que não seja vazia nem só com espaços (o título é devolvido sem normalização);
- `prioridade`: `int` (não `bool`) de 0 a 5, inclusive;
- `concluida`: `bool`.

Entradas inválidas são **descartadas silenciosamente**: campos ausentes, tipos errados, prioridades fora da faixa, itens que não são dicionários. Não há erro nem aviso.

Se a entrada inteira não for uma `list`, a função devolve `[]`.

## Cópia
- Cada item devolvido é `dict(original)`: uma cópia rasa nova por ocorrência, mesmo quando o mesmo dicionário aparece várias vezes na entrada.
- Campos extras são preservados; objetos aninhados (ex.: lista em `etiquetas`) são compartilhados com a entrada, não copiados (comportamento de cópia rasa).
- A lista e os dicionários recebidos não são modificados.

## Desempenho
- Complexidade O(n log n) pela ordenação; adequada para as 30.000 ocorrências previstas.
