# Tarefa: converter texto de duração em segundos

Crie o arquivo `solucao.py` no diretório de trabalho com a função:

```python
def parse_duracao(texto: str) -> int:
    ...
```

A função recebe uma duração escrita por humanos e retorna o total em **segundos** (`int`).

## Formato aceito

- A duração é formada por 1 a 4 componentes `<inteiro><unidade>`, onde o inteiro é composto
  só por dígitos `0-9` (zeros à esquerda são permitidos) e a unidade é uma de:
  - `d` = dias (86400 s), `h` = horas (3600 s), `m` = minutos (60 s), `s` = segundos (1 s).
- Unidades aceitas em maiúsculas ou minúsculas (`1H30M` == `1h30m`).
- Os componentes devem aparecer na ordem `d`, `h`, `m`, `s`, cada unidade **no máximo uma vez**
  (componentes podem ser omitidos: `1d5s` é válido).
- Componentes podem estar colados (`1h30m`) ou separados por espaços em branco (`1h 30m`).
  Espaços em branco no início/fim são ignorados. **Não** pode haver espaço entre o número e sua unidade (`1 h` é inválido).
- Não há limite por componente: `90m` == 5400.

## Erros

- `TypeError` se `texto` não for `str`.
- `ValueError` para qualquer entrada fora do formato: string vazia/só espaços, número sem unidade
  (`"90"`), unidade desconhecida (`"5x"`), números negativos ou decimais (`"-5s"`, `"1.5h"`),
  ordem errada (`"30m1h"`), unidade repetida (`"1h2h"`) ou texto extra.

## Exemplos

| entrada | saída |
|---|---|
| `"45s"` | `45` |
| `"1h30m"` | `5400` |
| `"2d 3h 4m 5s"` | `183845` |
| `"  0s  "` | `0` |
| `"1D1S"` | `86401` |

Use apenas a biblioteca padrão (Python 3.11).
