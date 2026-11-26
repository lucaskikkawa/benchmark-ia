# Suposições de Projeto

Este documento registra as decisões tomadas para os pontos em aberto da função `classificar_mensagem(texto: str) -> dict` em `solucao.py`.

## Categorias suportadas

Além de `"vazia"` (reservada exclusivamente para `texto == ""`), a classificação utiliza seis categorias, todas em minúsculas e sem acentos:

- `"reclamacao"`: mensagens relatando falhas, erros, atrasos, defeitos ou insatisfação.
- `"pedido"`: solicitações diretas de ação, suporte, alteração ou envio.
- `"duvida"`: perguntas ou pedidos de explicação.
- `"elogio"`: agradecimentos, aprovação ou feedback positivo.
- `"sem_conteudo"`: textos não vazios sem nenhum caractere alfanumérico e sem ponto de interrogação.
- `"outro"`: qualquer outra mensagem não vazia com conteúdo alfanumérico que não dispare as regras acima (por exemplo, `"vazia"`, `"ok"` ou `"URGENTE"` isolado).

## Sinais e desempate entre categorias

A classificação usa busca por termos inteiros (`\b...\b` via `re`) após normalização:

- `"reclamacao"`: `erro`, `problema`, `defeito`, `quebrado`, `quebrada`, `falha`, `lento`, `lenta`, `horrivel`, `pessimo`, `pessima`, `nao funciona`, `reclamacao`, `reclamar`, `atraso`, `atrasado`, `atrasada`, `cobranca indevida`, `cancelar`, `insatisfeito`, `insatisfeita`.
- `"pedido"`: `por favor`, `preciso`, `gostaria`, `quero`, `solicito`, `solicitacao`, `enviar`, `envie`, `mandar`, `mande`, `atualizar`, `atualize`, `alterar`, `altere`, `ajuda`, `ajudar`, `ajude`, `suporte`, `pedido`.
- `"duvida"`: presença do caractere `"?"` ou os termos `como`, `quando`, `onde`, `qual`, `quais`, `porque`, `por que`, `duvida`, `duvidas`, `funciona`, `explica`, `explicar`, `entender`, `posso`, `consigo`.
- `"elogio"`: `obrigado`, `obrigada`, `parabens`, `excelente`, `otimo`, `otima`, `maravilhoso`, `maravilhosa`, `perfeito`, `perfeita`, `adorei`, `gostei`, `elogio`, `recomendo`, `valeu`.

Quando uma mensagem casa com múltiplas categorias, vence a de maior prioridade na ordem fixa:
`reclamacao` > `pedido` > `duvida` > `elogio`.
A prioridade favorece tratar reclamações e solicitações acionáveis antes de dúvidas ou elogios (por exemplo, `"Obrigado, mas deu erro"` resulta em `"reclamacao"`).

## Maiúsculas e acentos na categoria

Para decidir `categoria`, o texto é convertido para NFD, caracteres combinantes são removidos e o resultado é convertido para minúsculas (`str.lower()`). Assim, `"DÚVIDA"` e `"duvida"` recebem o mesmo tratamento.

Essa normalização é isolada da verificação de `urgente` e do cálculo de `tamanho`, que operam diretamente sobre o `texto` original, preservando integralmente as regras fechadas (`"URGENTE"` exato e `len(texto)` em code points, inclusive com surrogates isolados como `"\ud800"`).

## Texto não vazio sem palavras

Textos com `len(texto) > 0` que não contenham `"?"` nem caracteres alfanuméricos (`ch.isalnum()`) são classificados como `"sem_conteudo"`. Isso cobre strings com apenas espaços (`"   "`), espaço inseparável (`"\u00a0"`), quebras de linha (`"\n"`), espaço de largura zero (`"\u200b"`), pontuação sem `?` (`"..."`, `"!!!"`), emojis isolados (`"🙂"`) e surrogates isolados (`"\ud800"`). Textos compostos apenas por interrogações (como `"???"`) caem em `"duvida"`.

## Campos extras no dicionário retornado

Optou-se por **não** incluir campos extras no dicionário retornado. A função devolve estritamente as três chaves especificadas (`"categoria"`, `"urgente"`, `"tamanho"`), mantendo o contrato simples, determinístico e sem inferências especulativas como idioma ou pontuação de confiança.
