# Tarefa: normalizar telefones brasileiros

O time de CRM tem uma base de contatos com telefones digitados de qualquer jeito e quer padronizá-los.
Crie `telefones.py` no diretório de trabalho com:

```python
def normalizar_telefone(texto: str) -> str: ...
def extrair_telefones(texto: str) -> list[str]: ...
```

## O que se sabe

- `normalizar_telefone` recebe **um** telefone e devolve no formato E.164 brasileiro:
  `+55` + DDD (2 dígitos) + número, só dígitos após o `+`.
- O telefone pode vir com ou sem o código do país `55` (com ou sem `+`), e com separadores
  comuns: espaços, hífens, pontos e parênteses — que podem aparecer repetidos ou combinados
  (`( 11 )  98765 - 4321` é válido).
- O DDD é sempre informado e tem 2 dígitos, nenhum deles `0` (`11` a `99`, exceto `20`, `30`, ..., `90`).
- Números fixos têm 8 dígitos e começam com `2`, `3`, `4` ou `5`; celulares têm 9 dígitos e começam com `9`.
  Qualquer outro tamanho ou dígito inicial é inválido (nunca complete nem corte dígitos).
- Se não der para interpretar o texto como telefone, levante `ValueError`.
- `extrair_telefones` recebe um texto livre (ex.: o campo "observações" de um contato) e devolve
  os telefones encontrados já normalizados, sem repetições, na ordem em que aparecem pela primeira vez.
  - Trechos numéricos que não formam um telefone válido (datas, CPFs, valores, CEPs, códigos) são
    ignorados sem erro; um telefone nunca é recortado de dentro de uma sequência maior de dígitos.
  - Telefones podem estar separados por vírgula, ponto e vírgula, barra, quebra de linha ou palavras,
    e podem vir seguidos de pontuação (`.`, `,`, `;`, `)`).

Exemplos:

```python
normalizar_telefone("+55 (11) 98765-4321")  # "+5511987654321"
normalizar_telefone("(21) 3456-7890")       # "+552134567890"
normalizar_telefone("11987654321")          # "+5511987654321"
normalizar_telefone("telefone")             # ValueError

extrair_telefones("Ligar para (11) 98765-4321 ou 21 3456-7890 à tarde")
# ["+5511987654321", "+552134567890"]
```

O resto não foi especificado pelo time. Onde houver dúvida (o que fazer com casos que o texto acima
não cobre), decida você mesmo e **registre cada decisão em `SUPOSICOES.md`** no diretório de trabalho:
a dúvida, a decisão tomada e o motivo. Use apenas a biblioteca padrão.
