# Suposições de Classificação de Mensagens

Este documento detalha as decisões tomadas para os pontos abertos da tarefa de classificação de mensagens.

## 1. Categorias existentes
Além da categoria obrigatória `"vazia"` (reservada unicamente para `texto == ""`), foram definidas as seguintes categorias:
- `"reclamacao"`: mensagens indicando problemas, insatisfação, defeitos ou cancelamentos.
- `"duvida"`: mensagens com questionamentos, pedidos de informação ou sinais de interrogação.
- `"pedido"`: mensagens voltadas a compras, encomendas, cotações ou solicitações comerciais.
- `"elogio"`: mensagens contendo felicitações, agradecimentos ou apreciações positivas.
- `"outro"`: mensagens que não se enquadram nas anteriores ou que não contenham termos classificáveis.

## 2. Palavras, sinais disparadores e resolução de conflitos
- **Dúvida**: disparada pela presença do caractere de interrogação `?` ou termos como `como`, `quando`, `onde`, `por que`, `porque`, `qual`, `quais`, `quem`, `quanto`, `duvida`, `ajuda`, `informacao`.
- **Reclamação**: disparada por termos como `problema`, `defeito`, `ruim`, `pessimo`, `erro`, `falha`, `cancelar`, `insatisfeito`, `demora`, `nao funciona`.
- **Pedido**: disparada por termos como `comprar`, `compra`, `pedido`, `encomenda`, `solicito`, `quero`, `preco`, `orcamento`, `cotacao`.
- **Elogio**: disparada por termos como `parabens`, `otimo`, `excelente`, `bom`, `adorei`, `gostei`, `maravilhoso`, `perfeito`, `obrigado`, `valeu`.

**Resolução de conflitos:** Quando uma mensagem corresponder a mais de uma categoria, adota-se a seguinte ordem decrescente de prioridade operacional:
1. `reclamacao` (prioridade máxima para contenção de atrito)
2. `duvida`
3. `pedido`
4. `elogio`
5. `outro`

## 3. Sensibilidade a maiúsculas e acentuação
- Para a **classificação de categoria**, a análise ignora maiúsculas e acentos (o texto passa por conversão para minúsculas e remoção de acentos via decomposição Unicode segura contra surrogates isolados).
- Para a flag **`urgente`**, a regra estrita do enunciado é preservada: sensível a maiúsculas (exatamente a substring `"URGENTE"` inalterada, sem normalização nem casefold).

## 4. Textos não vazios sem palavras (espaços, pontuação)
Textos que contenham apenas caracteres de espaço em branco (como espaços simples, `\u00a0`, `\u200b`, quebras de linha `\n`) ou pontuações sem significado específico (por exemplo, `!`, `.`, `...`, `-`) são classificados como `"outro"`, garantindo que apenas a string vazia (`""`) utilize `"vazia"`. Se contiverem `?`, são classificados como `"duvida"`.

## 5. Campos extras no dicionário de retorno
Optou-se por retornar estritamente os campos essenciais exigidos: `"categoria"`, `"urgente"` e `"tamanho"`. Nenhum campo adicional (como confiança ou idioma) foi adicionado para preservar a simplicidade e manter compatibilidade estrita com a interface esperada.
