# Tarefa: CLI de frequência de palavras

Crie o script `freq.py` no diretório de trabalho, executável como `python freq.py [opções] ARQUIVO`,
usando `argparse` e apenas a biblioteca padrão. Ele conta as palavras de um arquivo de texto e
imprime as mais frequentes.

## Argumentos

| argumento | descrição |
|---|---|
| `ARQUIVO` (posicional, obrigatório) | caminho do arquivo de texto (UTF-8). `-` significa ler da entrada padrão. |
| `-n N`, `--top N` | quantas palavras mostrar; inteiro `>= 1`; padrão `10`. |
| `-m K`, `--min-len K` | ignora palavras com menos de `K` caracteres; inteiro `>= 1`; padrão `1`. |
| `-i`, `--ignore-case` | converte as palavras para minúsculas antes de contar. Sem a flag, `Casa` e `casa` são palavras diferentes. |
| `-x PALAVRA`, `--excluir PALAVRA` | ignora essa palavra; pode ser repetida (`-x a -x o`). Com `-i`, a palavra excluída também passa por `str.lower()` antes da comparação; sem `-i`, a comparação é exata. |
| `--formato {texto,json}` | formato de saída; padrão `texto`. |

## Regras

- **Palavra** = sequência máxima de letras Unicode (dígitos, `_` e pontuação separam palavras),
  isto é, o que casa com a regex `[^\W\d_]+` aplicada ao texto **original** (sem normalização Unicode).
- Ordem de processamento: (1) extrair as palavras do texto original; (2) com `-i`, aplicar `str.lower()`
  a **cada palavra extraída** (não use `casefold`; `Straße` e `STRASSE` continuam diferentes); (3) descartar
  as com menos de `K` caracteres e as excluídas por `-x`; (4) contar.
- Ordenação: contagem decrescente; empate → palavra em ordem crescente (comparação simples de `str`).
- Saída `texto`: uma linha por palavra no formato `palavra<TAB>contagem` (ex.: `casa\t3`), em stdout.
- Saída `json`: uma lista JSON em stdout, ex.: `[{"palavra": "casa", "contagem": 3}]`.
- Sem palavras a mostrar: saída `texto` vazia (nada impresso); `json` imprime `[]`. Código de saída 0.

## Erros e códigos de saída

- `0`: sucesso.
- `2`: argumentos inválidos (opção desconhecida, `ARQUIVO` ausente, `N`/`K` não inteiros ou `< 1`,
  formato inválido) — use os erros do próprio `argparse` (`parser.error`/`type=`), que imprimem a
  mensagem de uso em stderr.
- `1`: erro ao ler a entrada (arquivo inexistente, é um diretório, sem permissão, conteúdo que não é
  UTF-8 válido — inclusive quando a entrada é a padrão, `-`). Imprima em **stderr** uma única linha
  começando com `erro: ` e nada em stdout. O resultado não pode depender da codificação/locale do
  terminal: a entrada (arquivo ou stdin) é sempre decodificada como UTF-8 estrito.

Exemplo:

```
$ printf 'A casa, a CASA; a casa!\n' > t.txt
$ python freq.py -i -n 2 t.txt
a	3
casa	3
```
