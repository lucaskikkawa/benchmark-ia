# Suposições de `classificar_mensagem`

## Núcleo (fixado pelo enunciado)

- `tamanho` = `len(texto)` em code points, sem `strip` nem normalização. Surrogates isolados (`"\ud800"`) não causam erro: o texto nunca é codificado.
- `urgente` = `"URGENTE" in texto`, sensível a maiúsculas, sem normalizar nem casefold, sem exigir palavra inteira. Lookalikes (ex.: `Е` cirílico) não contam.
- `""` (e só ela) → `categoria == "vazia"`, `urgente False`, `tamanho 0`.
- Entrada que não é `str` (incluindo `None`, `bytes`, `bytearray`, `int`) → `TypeError`. Subclasses de `str` são aceitas.

## Categorias

`vazia`, `reclamacao`, `pedido`, `duvida`, `elogio`, `sem_palavras`, `outro` (nomes sem acento, ASCII).

- `sem_palavras`: texto não vazio sem nenhuma letra ou dígito (só espaços, `\n`, ` `, `​`, pontuação, emoji...). Nunca usa `vazia`.
- `outro`: tem palavras, mas nenhum gatilho casou.

## Gatilhos

- Listas fixas de palavras e algumas expressões de duas palavras em `_GATILHOS` (`solucao.py`). Exemplos:
  - reclamacao: "problema", "defeito", "péssimo", "não funciona", "atraso", "cancelar"...
  - pedido: "quero", "gostaria", "preciso", "solicito", "por favor"...
  - duvida: "como", "quando", "qual", "por que", "dúvida"... e o caractere `?` vale 1 ponto.
  - elogio: "obrigado", "parabéns", "ótimo", "excelente", "adorei"...
- Casamento por palavra inteira (tokens `[^\W_]+`), não por substring: "bom" não casa em "bombeiro".
- A palavra "URGENTE" não influencia a categoria; só o campo `urgente`.

## Maiúsculas e acentos

- A classificação ignora maiúsculas (`casefold`) e acentos (NFD + remoção de marcas combinantes). Essa normalização é usada só para escolher a categoria; não afeta `tamanho` nem `urgente`.

## Mais de uma categoria

- Cada categoria recebe 1 ponto por gatilho distinto encontrado (mais 1 para `duvida` se houver `?`).
- Vence a de maior pontuação; empate é resolvido pela prioridade fixa `reclamacao > pedido > duvida > elogio` (reclamação primeiro por ser a que mais pede ação).

## Campos extras

- `categorias_casadas`: lista (na ordem de prioridade) de todas as categorias com pelo menos um gatilho; vazia para `vazia`, `sem_palavras` e `outro`.
- Não há campo de idioma nem de confiança; o vocabulário assume português.
