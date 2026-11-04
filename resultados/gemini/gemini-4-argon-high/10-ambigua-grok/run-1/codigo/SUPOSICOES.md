# Suposições e Decisões de Projeto (`SUPOSICOES.md`)

Este documento registra as decisões tomadas para os pontos abertos da especificação de `classificar_mensagem(texto: str) -> dict`.

## 1. Categorias existentes
Além da categoria `"vazia"` (exclusiva para `texto == ""`), foram definidas as seguintes categorias (todas em ASCII minúsculo, sem acentos):
- `"sem_conteudo"`: mensagens não vazias que não possuem nenhum caractere alfanumérico (`ch.isalnum()`).
- `"reclamacao"`: relatos de problemas, falhas, erros ou insatisfação.
- `"pedido"`: solicitações de ação, ajuda ou suporte.
- `"duvida"`: perguntas ou pedidos de esclarecimento.
- `"elogio"`: agradecimentos, cumprimentos positivos ou manifestações de satisfação.
- `"outro"`: categoria padrão (*fallback*) para qualquer mensagem com conteúdo alfanumérico que não se enquadre nas categorias acima (incluindo o texto literal `"vazia"`).

## 2. Sinais, palavras-chave e regra de desempate (precedência)
Quando um texto contém palavras ou sinais de mais de uma categoria, aplica-se uma ordem estrita de prioridade (precedência):
1. **`"reclamacao"`** (maior prioridade): disparada pelas palavras `erro(s)`, `problema(s)`, `falha(s)`, `bug(s)`, `defeito(s)`, `reclamacao`, `reclamar`, `ruim`, `pessimo(a)`, `lento(a)`, `travou`, `travando`, `quebrado(a)`, `indisponivel`, `inoperante` ou pelas expressões `"nao funciona"`, `"parou de funcionar"`, `"fora do ar"`.
2. **`"pedido"`**: disparada pelas palavras `pedido`, `solicito`, `solicitacao`, `preciso`, `quero`, `favor`, `ajuda`, `suporte`, `enviar`, `envie`, `cancelar`, `cancele`, `alterar`, `atualizar`, `liberar`, `desbloquear`.
3. **`"duvida"`**: disparada pela presença do ponto de interrogação (`?`) em textos com caracteres alfanuméricos, pelas palavras `duvida(s)`, `como`, `onde`, `quando`, `qual`, `quais`, `porque`, `quem`, `quanto` ou pelas expressões `"por que"`, `"pode informar"`, `"sabe dizer"`.
4. **`"elogio"`**: disparada pelas palavras `elogio`, `obrigado(a)`, `parabens`, `excelente`, `otimo(a)`, `perfeito(a)`, `bom`, `boa`, `adorei`, `gostei`, `satisfeito(a)`.
5. **`"outro"`** (menor prioridade): atribuída quando nenhuma das regras anteriores é satisfeita.

## 3. Tratamento de maiúsculas e acentos
- **Para a escolha da `categoria`**: a classificação **ignora maiúsculas/minúsculas e acentos**. O texto passa por conversão para minúsculas (`lower()`) e decomposição Unicode (`NFD`) com remoção de marcas combinantes (`Mn`) antes da extração de tokens alfanuméricos. Assim, `"DÚVIDA"`, `"dúvida"` e `"duvida"` produzem a mesma categoria `"duvida"`.
- **Para `urgente` e `tamanho`**: nenhuma normalização ou alteração de caixa é aplicada. `urgente` verifica estritamente a presença da substring exata `"URGENTE"` no `texto` original, e `tamanho` é calculado diretamente via `len(texto)`.

## 4. Textos não vazios sem palavras (espaços, pontuação, símbolos, surrogates)
Qualquer string `texto != ""` que não contenha ao menos um caractere alfanumérico (`not any(ch.isalnum() for ch in texto)`) — como apenas espaços (`"   "`, `"\u00a0"`), quebras de linha (`"\n"`), caracteres de largura zero (`"\u200b"`), pontuação isolada (`"???"`, `"..."`), emojis (`"🙂"`) ou *lone surrogates* (`"\ud800"`) — recebe a categoria `"sem_conteudo"`, garantindo que nunca receba `"vazia"`.

## 5. Campos do dicionário retornado
Optou-se por **não incluir campos extras** no dicionário de retorno. A função devolve exclusivamente as três chaves especificadas no contrato (`"categoria"`, `"urgente"` e `"tamanho"`), mantendo a interface enxuta e previsível.
