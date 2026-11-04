# Suposições e Decisões de Projeto (`SUPOSICOES.md`)

Este documento registra as decisões tomadas para os pontos deixados em aberto na especificação de `classificar_mensagem(texto: str) -> dict`.

## 1. Categorias disponíveis além de `"vazia"`

Além de `"vazia"` (exclusiva para `texto == ""`), o classificador utiliza as seguintes categorias:

- `"reclamacao"`: mensagens relatando erros, falhas, problemas ou insatisfação.
- `"duvida"`: perguntas ou questionamentos diretos.
- `"pedido"`: solicitações de ação, auxílio ou atendimento.
- `"elogio"`: agradecimentos e manifestações positivas.
- `"sem_conteudo"`: mensagens não vazias que não contêm caracteres alfanuméricos (apenas espaços, quebras de linha, caracteres invisíveis ou símbolos sem ponto de interrogação).
- `"outro"`: qualquer mensagem com palavras/caracteres alfanuméricos que não se enquadre nas categorias específicas acima (por exemplo, `"vazia"`, `"olá"`, `"123"`).

## 2. Palavras-chave, sinais e regra de desempate (precedência)

A avaliação segue uma ordem estrita de prioridade (a primeira regra que casar define a categoria):

1. **String vazia (`""`)**: retorna `"vazia"`.
2. **Sem tokens alfanuméricos**:
   - Se contiver o sinal `"?"`, retorna `"duvida"`.
   - Caso contrário (apenas espaços em branco como `" "`, `"\n"`, `"\u00a0"`, `"\u200b"`, emojis, surrogates isolados ou pontuações diversas), retorna `"sem_conteudo"`.
3. **`"reclamacao"`**: disparada se houver qualquer uma das palavras: `erro`, `problema`, `defeito`, `falha`, `reclamacao`, `reclamar`, `ruim`, `pessimo`, `quebrado`, `demora`, `atraso`.
4. **`"duvida"`**: disparada se o texto contiver `"?"`, a expressão `"por que"`, ou qualquer uma das palavras: `como`, `quando`, `onde`, `qual`, `quais`, `quem`, `duvida`, `porque`, `poque`.
5. **`"pedido"`**: disparada se houver qualquer uma das palavras: `solicito`, `pedido`, `favor`, `preciso`, `quero`, `gostaria`, `enviar`, `cancelar`.
6. **`"elogio"`**: disparada se houver qualquer uma das palavras: `parabens`, `excelente`, `otimo`, `maravilhoso`, `obrigado`, `obrigada`, `elogio`, `perfeito`, `adorei`, `gostei`.
7. **`"outro"`**: valor padrão (fallback) quando há caracteres alfanuméricos, mas nenhuma regra anterior foi acionada.

Quando o texto casa com mais de uma categoria (por exemplo, uma reclamação que termina com `"?"` ou contém `"quero"`), prevalece a categoria de maior prioridade na ordem acima (`reclamacao` > `duvida` > `pedido` > `elogio` > `outro`).

## 3. Tratamento de maiúsculas e acentos

- **Na escolha da `categoria`**: a classificação ignora diferenças entre maiúsculas e minúsculas (`texto.lower()`) e remove acentos/diacríticos via decomposição Unicode (`NFD`, descartando caracteres da categoria `Mn`). Assim, `"DÚVIDA"`, `"dúvida"` e `"duvida"` são tratados de forma idêntica.
- **No cálculo de `urgente`**: permanece estritamente sensível a maiúsculas, acentos e code points exatos (`"URGENTE" in texto`), sem normalização nem `casefold`, conforme exigido pela especificação.
- **No cálculo de `tamanho`**: calculado diretamente com `len(texto)` sobre a string original sem nenhuma alteração.

## 4. Textos não vazios sem palavras

Textos com `len(texto) > 0` que contêm apenas espaços (`" "`, `"\t"`, `"\n"`, `"\u00a0"`), caracteres de largura zero (`"\u200b"`), surrogates isolados (`"\ud800"`) ou sinais de pontuação (exceto `"?"`, que indica `"duvida"`) recebem a categoria `"sem_conteudo"`, garantindo que nunca recebam `"vazia"`.

## 5. Campos do dicionário de retorno

Optou-se por manter o dicionário enxuto contendo apenas as três chaves padronizadas (`"categoria"`, `"urgente"` e `"tamanho"`), sem campos extras.
