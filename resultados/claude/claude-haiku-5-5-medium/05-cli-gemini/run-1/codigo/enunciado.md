# 05 - Ferramenta CLI de Contagem e Métricas de Texto

Implemente uma ferramenta de linha de comando no arquivo `contatexto.py` na raiz do seu diretório de trabalho.

## Invocação

```bash
python contatexto.py [ARQUIVO] [FLAGS]
```

A CLI deve utilizar a biblioteca padrão `argparse`.

## Argumentos e Flags

- `ARQUIVO` (posicional, obrigatório): caminho para o arquivo de texto UTF-8 a ser analisado.
- `-l`, `--linhas` (flag booleana): contabiliza a quantidade de linhas no arquivo (utilizando quebras de linha/`splitlines()`).
- `-p`, `--palavras` (flag booleana): contabiliza o total de palavras (tokens separados por espaços em branco via `split()`).
- `-c`, `--chars` (flag booleana): contabiliza o total de caracteres no arquivo (`len(conteudo)`).
- `--top N` (inteiro >= 1): lista as `N` palavras mais frequentes.
  - Para o top palavras, tokens são convertidos para minúsculas e caracteres de pontuação nas pontas (`.,!?;:"'()[]{}`) são removidos via `.strip(...)`. Tokens vazios resultantes são descartados.
  - Em caso de empate de frequência, ordene as palavras alfabeticamente.
- `--json` (flag booleana): formata o resultado como um objeto JSON.
- `-o`, `--saida CAMINHO` (string): grava a saída no caminho especificado em vez de imprimir o resultado na stdout. Quando esta flag for utilizada, a CLI deve escrever o resultado no arquivo e imprimir na stdout exatamente: `Salvo em CAMINHO\n`. Caso as pastas pai do arquivo de saída não existam, crie-as automaticamente.

### Regras de Exibição das Métricas
1. Se **nenhuma** das flags de métrica (`-l`, `-p`, `-c`, `--top`) for fornecida, a ferramenta deve exibir **linhas, palavras e caracteres** por padrão.
2. Se **ao menos uma** flag de métrica for informada, ela deve exibir **estritamente** as métricas selecionadas.

### Formato de Saída em Texto (padrão)
Cada métrica selecionada é exibida em uma linha:
```
Linhas: 10
Palavras: 50
Caracteres: 320
Top Palavras:
  - python: 6
  - codigo: 4
```

### Formato de Saída em JSON (`--json`)
Um objeto JSON indentado (`indent=2`, `ensure_ascii=False`) contendo apenas as chaves das métricas selecionadas:
- `"linhas"`: int
- `"palavras"`: int
- `"caracteres"`: int
- `"top_palavras"`: lista de objetos `{"palavra": str, "ocorrencias": int}`

### Códigos de Saída (Exit Codes)
- `0`: Operação concluída com sucesso.
- `1`: Erro operacional (ex.: arquivo não existe, caminho aponta para um diretório em vez de arquivo regular, ou erro de leitura / decodificação). Deve exibir mensagem de erro na `stderr` iniciando com `Erro` (por exemplo, `Erro: ...` ou `Erro ao ler arquivo: ...`) e terminar com código 1.
- `2`: Erro de sintaxe nos argumentos (ex.: arquivo ausente, flag inexistente, ou `--top` com valor menor que 1).
