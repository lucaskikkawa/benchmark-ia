# Tarefa: consolidar chamados e SLA

Crie `solucao.py` no diretório de trabalho com a função abaixo. Só a biblioteca padrão. Os arquivos de entrada são passados por caminho; não deixe amostra obrigatória no repositório.

```python
def consolidar(caminho_csv: str, caminho_sla: str, caminho_saida: str) -> dict:
    """Lê os chamados e o SLA, grava o resumo em JSON e devolve o mesmo dict."""
```

## `chamados` CSV

Codificação UTF-8. Cabeçalho **exato**, nesta ordem:

```text
id,equipe,aberto_em,fechado_em,prioridade
```

- Codificação UTF-8 **sem BOM**. Um `U+FEFF` no início torna o cabeçalho diferente e é `ValueError` (não use `utf-8-sig`).
- Aceite fim de linha `\n` e `\r\n`. Campos com vírgula ou aspas seguem o `csv` padrão (`"São, Paulo"` é um campo).
- Linhas em branco, ou em que **todos** os campos ficam vazios depois do `strip` (por exemplo `,,,,`), são ignoradas.
- Os cinco campos são lidos com `csv` e depois cada um sofre `strip`. O cabeçalho é comparado **antes** do strip e tem de ser exato.
- `id` e `equipe` não podem ficar vazios depois do strip. Espaço no meio permanece: `"a b"` é um id válido.
- `id` é único **depois** do strip (`"a"` e `" a "` são duplicata → `ValueError`).
- Equipes também se agrupam pelo nome já com strip: `" n1 "` e `"n1"` são a mesma equipe.
- `aberto_em` e `fechado_em` usam o formato `YYYY-MM-DDTHH:MM` (16 caracteres). Data inexistente ou formato diferente → `ValueError`. A duração pode cruzar dias, meses e anos.
- `fechado_em` anterior a `aberto_em` → `ValueError`. Iguais são válidos (duração 0).
- A duração em minutos é um inteiro: diferença exata entre os dois instantes, sem segundos.
- `prioridade` é exatamente `baixa`, `media` ou `alta` **depois** do strip. `" alta "` é válida. `"Alta"` não é.
- Cabeçalho diferente, número de colunas diferente, arquivo vazio ou sem cabeçalho → `ValueError`. JSON de SLA inválido ou vazio também é `ValueError`.
- Arquivo ausente → `FileNotFoundError` (o de `open`).

## `sla` JSON

```json
{"limites_minutos": {"baixa": 480, "media": 240, "alta": 60}}
```

- Objeto com exatamente a chave `limites_minutos`.
- Esse objeto tem exatamente as três prioridades.
- Cada limite é `int` ≥ 1. `bool` e `float` não servem.
- Qualquer desvio → `ValueError`.

Um chamado **estoura** quando `duracao_minutos > limite` da prioridade. Igual ao limite não estoura.

## Saída

Grave `caminho_saida` em UTF-8, `json` com `ensure_ascii=False`, `indent=2` e uma quebra de linha no final. Devolva o mesmo conteúdo do arquivo.

```python
{
    "equipes": [
        {
            "equipe": "n1",
            "chamados": 2,
            "estourados": 1,
            "tempo_medio_minutos": 45,
            "pior_id": "a1",
        }
    ]
}
```

- Entre no resumo apenas equipes que tiveram pelo menos um chamado válido.
- `equipes` ordenada pelo nome com `sorted` padrão (code point, sem locale): `"A"` vem antes de `"a"`, `"São Paulo"` vem antes de `"alfa"`.
- As chaves de cada equipe, nesta ordem, são `equipe`, `chamados`, `estourados`, `tempo_medio_minutos`, `pior_id`. A raiz tem só `equipes`. O arquivo é exatamente `json.dumps(..., ensure_ascii=False, indent=2) + "\n"`.
- `chamados` é a quantidade.
- `estourados` é quantos estouraram o SLA.
- `tempo_medio_minutos` é a divisão inteira `soma das durações // chamados` (piso, para números ≥ 0).
- `pior_id` é o `id` de maior duração. Empate: menor `id` na ordem lexicográfica de `str` (`"a10" < "a2"` é verdadeiro; não é ordem numérica).

CSV só com cabeçalho (e linhas em branco) produz `{"equipes": []}`.

## Exemplo

SLA com `alta` = 60. CSV:

```text
id,equipe,aberto_em,fechado_em,prioridade
a1,n1,2024-03-01T10:00,2024-03-01T11:01,alta
b2,n1,2024-03-01T10:00,2024-03-01T10:30,alta
```

`a1` dura 61 minutos (estoura), `b2` dura 30 (não estoura). Média `(61 + 30) // 2 = 45`. Pior id: `a1`.

Dois chamados da mesma equipe com a mesma duração e ids `a10` e `a2`: `pior_id` é `a10`.
