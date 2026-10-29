# Tarefa: resumir vendas de um CSV em JSON

Crie `solucao.py` no diretório de trabalho com a função:

```python
from pathlib import Path

def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    ...
```

Ela lê um CSV de vendas (`entrada`), agrega os dados, **escreve** o resumo como JSON em `saida`
(UTF-8) e **retorna** o mesmo resumo como `dict`. Há um arquivo de exemplo em `vendas_exemplo.csv`.

## Entrada

CSV em UTF-8 (o arquivo **pode** começar com BOM UTF-8, comum em planilhas exportadas), separador
vírgula, aspas duplas no padrão CSV (campos entre aspas podem conter vírgulas e quebras de linha), com
cabeçalho. Colunas obrigatórias (podem vir em qualquer ordem e pode haver colunas extras, que são
ignoradas): `data,regiao,produto,quantidade,preco_unitario,status`. Os nomes no cabeçalho são comparados
após remover espaços nas bordas, diferenciando maiúsculas/minúsculas.

- Falta alguma coluna obrigatória (inclusive arquivo totalmente vazio, sem cabeçalho) → `ValueError`.
- Arquivo inexistente → `FileNotFoundError`.
- Em caso de erro, `saida` **não** deve ser criado nem alterado.

## Regras, aplicadas linha a linha

1. Remova espaços nas bordas de todos os valores.
2. Uma linha é **inválida** se: tiver número de campos diferente do cabeçalho; `regiao` ou `produto`
   vazio; `quantidade` não for inteiro (`int(...)`) ou for `<= 0`; `preco_unitario` não for número
   com ponto decimal (`float(...)`, ex. `"2.50"`; `"2,50"` é inválido), não for finito (`nan`, `inf`)
   ou for `< 0`. A conversão é exatamente a de `int(valor)`/`float(valor)` do Python sobre o valor sem
   espaços nas bordas (ex.: `"+3"` e `"007"` são quantidades válidas; `"1e2"` é preço válido).
   Linhas inválidas são contadas em `linhas_invalidas` e descartadas, **independentemente do status**.
   Linhas totalmente vazias são ignoradas (não contam como inválidas).
3. Das linhas válidas, só entram na agregação as com `status` igual a `concluida` (sem diferenciar
   maiúsculas/minúsculas; `concluída`, com acento, **não** é igual). As demais são ignoradas sem contar como inválidas.
4. Agregue por `regiao` (valor exato após strip, diferenciando maiúsculas):
   - `quantidade_total`: soma das quantidades;
   - `total_vendas`: soma de `quantidade * preco_unitario`, arredondada a 2 casas (`round(x, 2)`) no final;
   - `produto_mais_vendido`: produto com maior quantidade somada na região; empate → o menor em ordem
     alfabética (comparação simples de `str`).

## Saída

```json
{
  "regioes": {
    "Norte": {"quantidade_total": 7, "total_vendas": 8.4, "produto_mais_vendido": "Lápis"},
    "Sul": {"quantidade_total": 12, "total_vendas": 55.0, "produto_mais_vendido": "Caneta"}
  },
  "total_geral": 63.4,
  "linhas_invalidas": 2
}
```

(este é o resultado para `vendas_exemplo.csv`). `regioes` com chaves em ordem alfabética (comparação
simples de `str`); `total_geral` = soma dos `total_vendas` das regiões, arredondada a 2 casas;
`total_vendas` e `total_geral` são sempre `float` (inclusive `0.0`) e `quantidade_total`/`linhas_invalidas`
sempre `int`. CSV só com cabeçalho → `{"regioes": {}, "total_geral": 0.0, "linhas_invalidas": 0}`.
Escreva o JSON com `ensure_ascii=False` e `indent=2`; crie os diretórios pais de `saida` se não
existirem. Use apenas a biblioteca padrão.
