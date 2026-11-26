# Suposições de implementação

Este documento registra as decisões tomadas para os pontos em aberto da tarefa de classificação de mensagens curtas em `solucao.py`.

## Categorias adotadas

Além de `"vazia"` (reservada exclusivamente para `texto == ""`), a função utiliza as seguintes categorias:

- `"sem_conteudo"`: mensagens não vazias que não contêm nenhum caractere alfanumérico (`str.isalnum()`), como espaços, quebras de linha, caracteres invisíveis (`\u00a0`, `\u200b`), pontuação isolada, emojis ou code points substitutos isolados (`\ud800`).
- `"reclamacao"`: relatos de erro, falha, defeito, atraso, insatisfação ou pedido de cancelamento/estorno.
- `"duvida"`: perguntas e pedidos de esclarecimento.
- `"pedido"`: solicitações de ação, alteração ou suporte.
- `"elogio"`: agradecimentos e avaliações positivas.
- `"outro"`: categoria padrão para qualquer texto com conteúdo alfanumérico que não corresponda às regras acima (incluindo textos literais como `"vazia"` ou `"URGENTE"` isolado).

## Sinais, palavras-chave e desempate

Cada categoria é acionada por expressões regulares com fronteiras de palavra (`\b`) sobre o texto normalizado (e pelo caractere `?` no caso de `"duvida"`):

- **`"reclamacao"`**: `reclamacao`, `reclamar`, `problema(s)`, `erro(s)`, `falha(s)`, `defeito`, `quebrado`, `quebrou`, `nao funciona`, `parou de funcionar`, `pessimo/a`, `horrivel`, `ruim`, `insatisfeito/a`, `atraso`, `atrasado/a`, `cobranca indevida`, `estorno`, `reembolso`, `cancelar`.
- **`"duvida"`**: ponto de interrogação (`?`), `duvida(s)`, `pergunta(s)`, `como faco`, `como funciona`, `onde encontro`, `qual e`, `quais sao`, `quando`, `porque`, `por que`, `saber se`, `poderia explicar`, `pode explicar`, `nao entendi`.
- **`"pedido"`**: `preciso`, `gostaria`, `quero`, `solicito`, `solicitacao`, `pedido`, `pedir`, `por favor`, `poderia`, `pode me`, `ajuda`, `ajudar`, `suporte`, `enviar`, `envie`, `atualizar`, `atualize`, `alterar`, `altere`, `liberar`, `libere`.
- **`"elogio"`**: `obrigado/a`, `valeu`, `agradeco`, `agradecimento`, `parabens`, `otimo/a`, `excelente`, `perfeito/a`, `muito bom/boa`, `adorei`, `amei`, `gostei`, `maravilhoso/a`, `satisfeito/a`, `eficiente`, `rapido`.

Quando uma mensagem casa com mais de uma categoria, aplica-se uma ordem fixa de prioridade:

`reclamacao` > `duvida` > `pedido` > `elogio` > `outro`

Essa precedência prioriza atendimentos com maior impacto operacional (por exemplo, uma mensagem que agradece mas relata um erro é classificada como `"reclamacao"`).

## Maiúsculas, acentos e regra de urgência

- A detecção de `categoria` ignora diferenças de maiúsculas/minúsculas e diacríticos: o texto passa por decomposição `unicodedata.normalize("NFKD", texto)`, remoção de marcas combinantes (`unicodedata.category(ch) != "Mn"`) e `.casefold()`.
- Essa normalização **nunca** é aplicada a `urgente` nem a `tamanho`: `urgente` verifica estritamente `"URGENTE" in texto` sobre a string original (sensível a maiúsculas e a homóglifos como `Е` cirílico) e `tamanho` usa `len(texto)` diretamente, sem `strip`, normalização ou codificação em bytes.

## Texto não vazio sem palavras

Qualquer string com `texto != ""` que não possua caracteres alfanuméricos (por exemplo, `"   "`, `"\n"`, `"\u00a0"`, `"\u200b"`, `"!!!"`, `"?"` ou `"🙂"`) é classificada como `"sem_conteudo"`, garantindo que nunca receba `"vazia"`.

## Campos extras no dicionário de retorno

Optou-se por retornar apenas as três chaves obrigatórias (`"categoria"`, `"urgente"`, `"tamanho"`), sem campos extras, para manter o contrato da função simples, enxuto e previsível.
