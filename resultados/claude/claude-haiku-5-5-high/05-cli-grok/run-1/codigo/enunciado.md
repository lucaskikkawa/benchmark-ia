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
- `proximo_id` inteiro ≥ 1 (`bool` não vale; `1.0` também não) e **maior** que todo `id` já usado (se não houver tarefas, só ≥ 1). Buracos são válidos: ids `1` e `3` com `proximo_id` `5` podem ser listados. O próximo `adicionar` grava id `5`, não `4` e não `max+1`;
- `tarefas` é uma lista de objetos com exatamente `id`, `titulo`, `prioridade`, `prazo`, `concluida`;
- `id` inteiro ≥ 1, único, não `bool`;
- `titulo` string não vazia depois das regras abaixo, sem `\n`, `\r` ou `\t`, e sem espaço nas pontas (o arquivo já deve estar normalizado; título `"  a  "` ou `"\n"` é inválido);
- `prioridade` é `baixa`, `media` ou `alta`;
- `prazo` é `null` ou `YYYY-MM-DD` de um dia real no calendário gregoriano de `datetime.date` (anos 1 a 9999). `2000-02-29` existe; `1900-02-29` e `2100-02-29` não;
- `concluida` é bool (`0` e `1` não valem).
- `id` duplicado, chave a mais ou chave a menos torna o arquivo inválido.

## adicionar

- `--titulo` é obrigatório. Vale o texto depois de `str.strip` (isso inclui espaços Unicode, como `\u00a0`). Se ficar vazio: `erro: titulo vazio`.
- `adicionar` em arquivo que já existe e é inválido: `erro: arquivo invalido`, e o arquivo **permanece byte a byte** como estava.
- `listar` não reescreve o arquivo.
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

- `--id` inteiro (`01` é o id `1`). Se não existir: `erro: id inexistente`.
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
