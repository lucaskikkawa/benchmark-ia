# Suposições

## Categorias
- `vazia`: somente para `texto == ""`.
- `reclamacao`, `pedido`, `duvida`, `elogio`: detectadas por palavras/expressões-chave (lista em `_CATEGORIAS` em `solucao.py`), casadas como palavra inteira (ex.: "erro" não casa dentro de "ferro").
- `outro`: texto com pelo menos uma palavra, mas que não casa nenhuma categoria.
- `sem_conteudo`: texto não vazio sem nenhum caractere de palavra (`\w`), ex.: só espaços, `"\n"`, `" "`, `"​"`, `"?!..."`, emoji isolado. Nunca usa `vazia`.

## Sinais e desempate
- Um `?` em texto com palavras, sem nenhuma palavra-chave casada, classifica como `duvida`.
- Quando casa mais de uma categoria, vence a de maior prioridade: `reclamacao` > `pedido` > `duvida` > `elogio`. Motivo: reclamação é o caso mais sensível para atendimento; elogio raramente exige ação.
- O texto literal `"vazia"` é uma palavra comum e cai em `outro`.

## Maiúsculas e acentos
- A classificação ignora maiúsculas (casefold) e acentos (NFKD + remoção de marcas combinantes) e colapsa espaços. Isso é feito só numa cópia interna.
- `urgente` NÃO usa essa normalização: é exatamente `"URGENTE" in texto`, sensível a maiúsculas.
- `tamanho` é `len(texto)` do texto original, sem strip nem normalização.
- Code points inválidos (surrogates soltos como `"\ud800"`) não causam erro; não há codificação para bytes.

## Campos extras
- `categorias_casadas`: lista (na ordem de prioridade) de todas as categorias cujas palavras-chave casaram; vazia para `vazia`, `sem_conteudo` e `outro`.
- Não há campos de idioma nem confiança; as palavras-chave assumem português.

## Tipos
- Qualquer valor que não seja instância de `str` (incluindo `None`, `bytes`, `bytearray`, `int`) levanta `TypeError`. Subclasses de `str` são aceitas.
