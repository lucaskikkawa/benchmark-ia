# Suposições e Decisões de Projeto

Este documento registra as decisões tomadas para os pontos em aberto na especificação da função `classificar_mensagem`.

## 1. Categorias existentes
Além da categoria `"vazia"` (reservada exclusivamente para a string vazia `""`), foram definidas as seguintes categorias:
- `"sem_palavras"`: para mensagens não vazias que não possuem caracteres alfanuméricos (apenas espaços em branco, quebras de linha, pontuação, símbolos ou caracteres de controle/surrogates).
- `"reclamacao"`: para mensagens indicando problemas, falhas, defeitos, atrasos ou insatisfação com serviços/produtos.
- `"duvida"`: para perguntas, dúvidas ou pedidos de esclarecimento e suporte.
- `"pedido"`: para solicitações de compra, contratação, envio ou novos pedidos.
- `"elogio"`: para mensagens de agradecimento, satisfação e elogios.
- `"outro"`: categoria padrão para mensagens que possuem palavras mas não se enquadram em nenhuma das categorias temáticas anteriores (por exemplo, a palavra `"vazia"`, saudações soltas sem intenção definida, etc.).

## 2. Gatilhos por categoria e desempate
- **Sinais e Palavras-chave**:
  - `"reclamacao"`: disparada por palavras como `defeito`, `problema`, `quebrado`, `ruim`, `pessimo`, `erro`, `reclamacao`, `falha`, `insatisfeito`, `horrivel`, `pior`, `cancelar`, `atraso`, `estragado`, `prejuizo`, `estorno` e expressões como `nao funciona`, `nao gostei`, `veio quebrado`, `veio errado`.
  - `"duvida"`: disparada pela presença do caractere de interrogação `?`, palavras como `como`, `quando`, `onde`, `porque`, `qual`, `quem`, `duvida`, `ajuda`, `saber`, `funciona`, `horario`, `preco`, `valor`, ou expressões como `por que`, `como faco`, `como funciona`, `quanto custa`.
  - `"pedido"`: disparada por palavras como `solicito`, `comprar`, `pedido`, `gostaria`, `quero`, `enviar`, `preciso`, `encomenda`, `adquirir`, `contratar`, `solicitacao`.
  - `"elogio"`: disparada por palavras como `obrigado`, `obrigada`, `parabens`, `otimo`, `excelente`, `bom`, `boa`, `perfeito`, `maravilhoso`, `adorei`, `show`, `agradeco`.
- **Resolução de Conflitos (Prioridade)**:
  Quando uma mensagem contiver termos ou sinais que atendam a múltiplos critérios, a classificação segue a seguinte ordem de precedência decrescente:
  1. `reclamacao` (máxima prioridade operacional em triagem de atendimento)
  2. `duvida`
  3. `pedido`
  4. `elogio`
  5. `outro`

## 3. Tratamento de maiúsculas e acentos
- A classificação temática das categorias ignora maiúsculas e acentos (comportamento case-insensitive e accent-insensitive).
- O texto para classificação temática é convertido para minúsculas e acentos latinos comuns são mapeados para suas formas não acentuadas via tabela de substituição direta (`str.translate`). Essa abordagem evita chamadas a `unicodedata.normalize`, prevenindo falhas de `UnicodeEncodeError` com caracteres surrogate isolados (ex.: `\ud800`).
- A regra do marcador `"URGENTE"` permanece estritamente sensível a maiúsculas (case-sensitive), sem qualquer normalização prévia e sem exigência de palavra completa, exatamente conforme exigido no enunciado.

## 4. Classificação de textos sem palavras (espaços, pontuação, símbolos)
- Qualquer texto diferente de `""` que não contenha caracteres alfanuméricos (ex.: `" "`, `"\u00a0"`, `"\n"`, `"!?. ,"` ou `"\ud800"`) é categorizado como `"sem_palavras"`.
- Dessa forma, respeita-se a regra de que a categoria `"vazia"` só é atribuída à string vazia exata `""`.

## 5. Campos extras no dicionário de retorno
- Optou-se por **não incluir campos extras** no dicionário de retorno, mantendo apenas `categoria`, `urgente` e `tamanho`.
- Essa escolha visa garantir simplicidade, foco e máxima compatibilidade com eventuais asserções estritas sobre as chaves do dicionário nos testes automatizados.
