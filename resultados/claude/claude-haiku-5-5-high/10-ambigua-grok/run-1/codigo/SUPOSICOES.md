# Suposições

Decisões tomadas nos pontos em aberto da tarefa de classificação de mensagens.

## Categorias

Além de `"vazia"` (somente para a string vazia), existem quatro categorias: `"reclamacao"`, `"pedido"`, `"duvida"` e `"elogio"`. Quando nenhuma casa, o texto cai em `"outro"`. Texto sem nenhum caractere alfanumérico (só espaços, pontuação, símbolos ou ` `) recebe `"indefinida"`. Nenhum texto não vazio usa `"vazia"`.

## Palavras que disparam cada categoria

- `reclamacao`: reclam, problema, defeito, "não funciona", péssimo, horrível, insatisfeito, "cobrado indevidamente".
- `pedido`: quero, preciso, solicit, peço, envi, gostaria, "por favor".
- `duvida`: o sinal `?`, ou as palavras dúvida, pergunta, como, qual, quando, onde (como palavra inteira).
- `elogio`: obrigado, parabéns, excelente, ótimo, adorei, gostei, maravilh, recomendo.

Quando o texto casa com mais de uma categoria, vence a primeira na ordem: reclamação, pedido, dúvida, elogio. Assim, "Por que isso não funciona?" vira `"reclamacao"`, não `"duvida"`. A categoria não depende da urgência: `"URGENTE"` não altera a categoria.

## Maiúsculas e acentos

A classificação ignora maiúsculas e acentos. O texto é decomposto (NFKD), os diacríticos são removidos e o resultado é passado para `casefold()` antes de os padrões rodarem. Essa normalização vale só para a categoria. A regra de `urgente` continua sensível a maiúsculas e usa o texto original, sem normalização.

## Texto sem palavra

Texto não vazio sem caractere alfanumérico (espaços, pontuação, emoji, `\n`, `​`) recebe `"indefinida"`. Essa categoria não é `"vazia"`, como exige a especificação. Texto alfanumérico que não casa com nenhuma palavra recebe `"outro"`.

## Campos extras

O dict tem apenas `categoria`, `urgente` e `tamanho`. Não há campos de idioma nem de confiança: detectar idioma ou calcular confiança exigiria heurísticas fora do escopo, e um valor chutado induziria a erro quem consome o dict.
