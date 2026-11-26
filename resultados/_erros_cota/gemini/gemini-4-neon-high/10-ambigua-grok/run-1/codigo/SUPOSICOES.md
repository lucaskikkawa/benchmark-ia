# Suposições e decisões de projeto

Este documento registra as decisões tomadas para os pontos em aberto da tarefa de classificação de mensagens curtas implementada em `solucao.py`.

## 1. Categorias disponíveis

Além da categoria obrigatória `"vazia"` (usada exclusivamente quando `texto == ""`), a função classifica mensagens nas seguintes categorias (todas em minúsculas e sem acento, para facilitar consumo programático):

- `"reclamacao"`: relatos de erro, falha, atraso, insatisfação, cancelamento ou pedido de reembolso/estorno.
- `"pedido"`: solicitações de ação, ajuda, suporte, alteração, atualização, envio ou agendamento.
- `"duvida"`: perguntas e pedidos de esclarecimento.
- `"elogio"`: agradecimentos e avaliações positivas.
- `"sem_conteudo"`: mensagens não vazias que não contêm nenhuma palavra (nenhum caractere alfanumérico).
- `"outro"`: mensagens não vazias com pelo menos uma palavra que não disparam nenhum sinal das categorias específicas acima (incluindo o texto literal `"vazia"`).

## 2. Sinais por categoria e critério de desempate

Cada categoria possui um conjunto de palavras-chave isoladas e expressões compostas (comparadas por limite de token, evitando falsos positivos como `"erro"` dentro de `"ferro"`):

- **`"reclamacao"`**: palavras como `reclamacao`, `reclamar`, `problema(s)`, `erro(s)`, `bug(s)`, `falha(s)`, `defeito`, `quebrado(a)`, `pessimo(a)`, `horrivel`, `ruim`, `atraso`, `atrasado(a)`, `cancelar`, `cancelamento`, `reembolso`, `estorno`, `insatisfeito(a)`; e expressões `nao funciona`, `nao funcionou`, `fora do ar`, `cobranca indevida`.
- **`"pedido"`**: palavras como `preciso`, `gostaria`, `quero`, `solicito`, `solicitacao`, `pedido`, `ajuda`, `ajudar`, `suporte`, `envie`, `enviar`, `atualize`, `atualizar`, `altere`, `alterar`, `verifique`, `verificar`, `libere`, `liberar`, `agendar`, `agendamento`; e a expressão `por favor`.
- **`"duvida"`**: presença do sinal `"?"` (desde que o texto tenha ao menos uma palavra), palavras como `duvida(s)`, `pergunta(s)`, `como`, `onde`, `quando`, `qual`, `quais`, `quanto`, `porque`; e expressões `por que`, `sera que`, `pode explicar`, `nao entendi`, `saber se`.
- **`"elogio"`**: palavras como `obrigado(a)`, `agradeco`, `parabens`, `excelente`, `otimo(a)`, `perfeito(a)`, `adorei`, `maravilhoso(a)`, `satisfeito(a)`, `elogio`, `valeu`; e expressões `muito bom`, `muito boa`, `bom trabalho`.

Quando uma mensagem casa com mais de uma categoria:

1. Calcula-se a pontuação de cada categoria como o número de sinais distintos encontrados (palavras-chave únicas + expressões compostas + o sinal `"?"` no caso de `"duvida"`).
2. Vence a categoria com maior pontuação.
3. Em caso de empate com pontuação positiva igual, aplica-se a ordem fixa de prioridade: `reclamacao` > `pedido` > `duvida` > `elogio` (priorizando problemas e solicitações acionáveis sobre dúvidas e elogios).

## 3. Normalização de maiúsculas e acentos

- Para a escolha de **`categoria`**, a classificação ignora maiúsculas/minúsculas e acentos: o texto passa por decomposição Unicode `NFD`, remoção de marcas combinantes (`unicodedata.category(ch) == "Mn"`) e `casefold()`. Assim, `"Reclamação"`, `"RECLAMACAO"` e `"reclamac\u0327a\u0303o"` recebem a mesma classificação.
- Essa normalização **não afeta** `tamanho` nem `urgente`: ambos são calculados diretamente sobre o `texto` original recebido (`len(texto)` e `"URGENTE" in texto`), preservando a contagem exata de code points, o suporte a surrogates isolados sem codificação UTF-8 e a sensibilidade exata a maiúsculas e homógrafos na verificação de `"URGENTE"`.

## 4. Textos não vazios sem palavras

Qualquer texto diferente de `""` que não possua nenhum caractere alfanumérico (por exemplo, espaços, quebras de linha, `\u00a0`, `\u200b`, pontuação pura como `"..."` ou `"???"`, emojis isolados como `"🙂"` ou surrogates isolados como `"\ud800"`) é classificado como `"sem_conteudo"`, nunca como `"vazia"`.

## 5. Campos extras no dicionário de retorno

Optou-se por retornar **apenas** as três chaves obrigatórias (`"categoria"`, `"urgente"` e `"tamanho"`), sem campos extras. Essa escolha mantém o contrato enxuto, previsível e livre de métricas heurísticas (como uma pontuação de confiança arbitrária) que não foram solicitadas.
