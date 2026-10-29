# Tarefa: CLI de agenda pessoal

Crie `agenda_cli.py` no diretório de trabalho. Ele é o programa completo: `argparse`, subcomandos, arquivo JSON e códigos de saída. Só a biblioteca padrão. Os testes chamam o script com `subprocess`.

```text
python agenda_cli.py adicionar --titulo TEXTO --prioridade baixa|media|alta [--prazo YYYY-MM-DD] --arquivo CAMINHO
python agenda_cli.py listar --arquivo CAMINHO [--prioridade baixa|media|alta] [--somente-abertas]
python agenda_cli.py concluir --id N --arquivo CAMINHO
```

`--arquivo` é obrigatório em todos. Sem subcomando, argumento desconhecido ou escolha inválida de prioridade: o `argparse` encerra com código 2.

## Arquivo JSON

Se `adicionar` receber um caminho que não existe, crie o arquivo. `listar` e `concluir` num caminho que não existe: código 2, stderr exatamente `erro: arquivo inexistente\n`, stdout vazio.

Formato (UTF-8, `indent=2`, `ensure_ascii=False`, quebra de linha final):

```json
{
  "proximo_id": 1,
  "tarefas": [
    {
      "id": 1,
      "titulo": "Comprar leite",
      "prioridade": "alta",
      "prazo": null,
      "concluida": false
    }
  ]
}
```

Na leitura, qualquer JSON que não siga esse formato gera `erro: arquivo invalido` (código 2). Exija:

- objeto com exatamente as chaves `proximo_id` e `tarefas`;
- `proximo_id` inteiro ≥ 1 (`bool` não vale) e **maior** que todo `id` já usado (se não houver tarefas, só ≥ 1);
- `tarefas` é uma lista de objetos com exatamente `id`, `titulo`, `prioridade`, `prazo`, `concluida`;
- `id` inteiro ≥ 1, único, não `bool`;
- `titulo` string não vazia, sem `\n`, `\r` ou `\t`;
- `prioridade` é `baixa`, `media` ou `alta`;
- `prazo` é `null` ou `YYYY-MM-DD` de um dia real;
- `concluida` é bool.

## adicionar

- `--titulo` é obrigatório. Vale o texto depois de `strip`. Se ficar vazio: `erro: titulo vazio`.
- Se o título (já sem espaços das pontas) contiver `\n`, `\r` ou `\t`: `erro: titulo invalido`.
- `--prioridade` obrigatória, uma das três opções.
- `--prazo` opcional. Se vier, tem de ser uma data real `YYYY-MM-DD`; senão `erro: prazo invalido`. Ausente grava `null`.
- O id novo é o `proximo_id` atual. Depois grave `proximo_id` incrementado em 1 e `concluida` false.
- Sucesso: stdout exatamente `ok id=N\n`, stderr vazio, código 0. Nada além disso.

## listar

Imprima uma tarefa por linha, sem cabeçalho, separador tab (`\t`), nesta ordem de colunas:

```text
id	prioridade	estado	prazo	titulo
```

- `estado` é `aberta` ou `concluida`.
- `prazo` nulo vira `-`.
- Ordem: prioridade `alta`, depois `media`, depois `baixa`; dentro da mesma prioridade, `id` crescente.
- `--prioridade` filtra uma prioridade. `--somente-abertas` tira as concluídas. Os dois filtros juntos são um E.
- Nenhuma tarefa (ou nenhuma após o filtro): stdout vazio (zero bytes), código 0.
- Cada linha impressa termina com `\n`.

## concluir

- `--id` inteiro. Se não existir: `erro: id inexistente`.
- Se já estiver concluída: `erro: ja concluida`.
- Senão marque `concluida` true, grave o arquivo e imprima `ok id=N\n` com código 0.

## Erros de regra

Código 2, stdout vazio, stderr exatamente `erro: MENSAGEM\n` (sem traceback), com uma destas mensagens:

- `titulo vazio`
- `titulo invalido`
- `prazo invalido`
- `arquivo inexistente`
- `arquivo invalido`
- `id inexistente`
- `ja concluida`
