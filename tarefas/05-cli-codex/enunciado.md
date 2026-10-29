# Contador de palavras pela linha de comando

Crie `cli.py`, executável por `python cli.py ARQUIVO [flags]`, usando `argparse`.
Exponha também `main(argv=None) -> int`, que retorna 0 em sucesso. No uso como
script, encerre com o código correspondente.

Leia ARQUIVO como UTF-8. Palavras são tokens de `str.split()` (qualquer espaço
em branco); pontuação faz parte do token. A CLI aceita:

- `--minimo N`: inteiro positivo, padrão 1; só exibe tokens de contagem >= N.
- `--ignorar-caixa`: aplica `str.casefold()` antes de contar.
- `--json`: escreve uma lista JSON de objetos `{'palavra': str, 'contagem': int}`.
- `-h` / `--help`: ajuda de argparse, código 0.

Ordene por contagem decrescente e depois pela palavra em ordem padrão de strings.
No formato padrão, cada linha é `PALAVRA\tCONTAGEM\n` (tab real).
Nenhum resultado gera stdout vazio no formato padrão e `[]` seguido de quebra
de linha no JSON. JSON deve preservar acentos sem escapes ASCII, em uma linha
com quebra de linha final. Não escreva mensagens de sucesso no stderr.

Arquivo ausente/ilegível ou UTF-8 inválido, argumento obrigatório ausente, flags
desconhecidas e mínimo não inteiro ou <= 0 devem resultar em código 2, stdout
vazio e mensagem não vazia no stderr, sem traceback. O texto exato da mensagem
é livre. Não há leitura de stdin, escrita de arquivos ou acesso à rede.

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
