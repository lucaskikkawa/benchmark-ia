# Suposições da solução

Este documento registra as decisões tomadas para os pontos em aberto da tarefa `classificar_mensagem(texto: str) -> dict` implementada em `solucao.py`.

## 1. Categorias adotadas

Além de `"vazia"` (reservada exclusivamente para `texto == ""`), a função utiliza as seguintes categorias:

- `"sem_conteudo"`: mensagens não vazias sem nenhum caractere alfanumérico.
- `"reclamacao"`: relatos de falha, defeito, atraso ou insatisfação.
- `"duvida"`: perguntas diretas ou pedidos de esclarecimento.
- `"pedido"`: solicitações de ação ou atendimento.
- `"elogio"`: agradecimentos ou comentários positivos.
- `"outro"`: mensagens com conteúdo textual que não correspondem a nenhuma das categorias anteriores.

## 2. Sinais por categoria e desempate

Cada categoria é acionada por expressões regulares com fronteiras de palavra (`\b`) aplicadas ao texto normalizado (além do sinal `?` para `"duvida"`):

- `"reclamacao"`: `erro(s)`, `problema(s)`, `falha(s)`, `quebrou`, `defeito`, `reclamacao`, `ruim`, `pessimo(a)`, `horrivel`, `travou`, `bug(s)`, `atraso`, `atrasado(a)`, `nao funciona`, `cobranca indevida`.
- `"duvida"`: `?`, `duvida(s)`, `como`, `quando`, `onde`, `qual`, `quais`, `por que`, `ajuda`, `explica`, `explicar`.
- `"pedido"`: `por favor`, `preciso`, `gostaria`, `solicito`, `quero`, `poderia`, `pode`, `enviar`, `envie`, `cancelar`, `alterar`, `atualizar`, `agendar`.
- `"elogio"`: `obrigado(a)`, `parabens`, `excelente`, `otimo(a)`, `adorei`, `perfeito(a)`, `maravilhoso(a)`, `valeu`, `bom trabalho`, `muito bom`.

Quando uma mensagem casa com mais de uma categoria, aplica-se uma ordem fixa de prioridade voltada a triagem de atendimento:

`reclamacao` > `duvida` > `pedido` > `elogio` > `outro`.

## 3. Sensibilidade a maiúsculas e acentos

A classificação de `categoria` ignora maiúsculas/minúsculas e acentos: o texto passa por decomposição `NFD`, remoção de marcas combinantes (`unicodedata.category(ch) == "Mn"`) e `casefold()`, sem jamais codificar em bytes (preservando compatibilidade com surrogates isolados como `"\ud800"`).

Essa normalização é usada **apenas** para decidir `categoria`. As regras fechadas de `tamanho` (`len(texto)` direto) e `urgente` (`"URGENTE" in texto`, sensível a maiúsculas e sem normalização) operam diretamente sobre a string original.

## 4. Textos não vazios sem palavras

Qualquer string diferente de `""` que não contenha caracteres alfanuméricos — como espaços, quebras de linha, `\u00a0`, `\u200b`, pontuação isolada, emojis ou surrogates — recebe a categoria `"sem_conteudo"`, nunca `"vazia"`.

Observação: a string `"?"` sozinha também não possui caracteres alfanuméricos, portanto é classificada como `"sem_conteudo"`. Já textos com palavras acompanhadas de `"?"` caem em `"duvida"` (salvo se houver termo de `"reclamacao"`).

## 5. Campos extras no dicionário retornado

Optou-se por retornar apenas as três chaves obrigatórias (`"categoria"`, `"urgente"` e `"tamanho"`), sem campos extras, mantendo o contrato mínimo, enxuto e previsível.
