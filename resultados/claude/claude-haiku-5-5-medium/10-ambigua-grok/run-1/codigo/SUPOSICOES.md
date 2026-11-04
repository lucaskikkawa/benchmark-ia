# Suposições

Categorias: `vazia` (só para `""`), `sem_palavras` (texto não vazio sem nenhum caractere alfanumérico, como espaços, `\n`, ` `, pontuação), `reclamacao`, `pedido`, `duvida`, `elogio` e `outro` (quando nenhuma palavra-chave casa).

Palavras-chave: cada categoria tem uma lista de substrings. `reclamacao` usa termos como "ruim", "problema", "erro", "demora"; `pedido` usa "quero", "preciso", "gostaria", "por favor"; `duvida` usa "?", "como ", "por que", "quando"; `elogio` usa "obrigado", "parabéns", "ótimo", "excelente".

Múltiplas categorias: a ordem da tupla define a prioridade, e vence a primeira que casar (reclamacao > pedido > duvida > elogio). Assim uma reclamação com pergunta sai como `reclamacao`, não como `duvida`.

Caixa e acentos: a categorização ignora maiúsculas e acentos (casefold e remoção de marcas NFKD), só para casar palavras-chave. A regra de `urgente` não usa esse processamento: continua sendo `"URGENTE" in texto`, sensível a maiúsculas e sem normalização, conforme o enunciado.

Campos extras: o dict tem apenas `categoria`, `urgente` e `tamanho`. Não há campo de confiança ou idioma.
