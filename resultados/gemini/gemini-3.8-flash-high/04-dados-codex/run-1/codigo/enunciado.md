# Resumo de vendas CSV em JSON

Crie `vendas.py` com:

```python
def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    ...
```

`entrada` e `saida` são caminhos str ou `pathlib.Path`, distintos. Leia um CSV UTF-8
com cabeçalho e as colunas obrigatórias `produto,quantidade,preco_centavos,status`
(em qualquer ordem; colunas extras são ignoradas). Use as regras de aspas de CSV.
Só processe linhas cujo status, após `strip().lower()`, seja `pago`; ignore as
outras antes de validar produto e números.

Nas linhas pagas, remova espaços externos do produto, que não pode ficar vazio.
Converta quantidade e preço em inteiros não negativos; valores inválidos lançam
`ValueError`. Agregue por produto (distinção de maiúsculas), somando quantidade e
`quantidade * preco_centavos`. Mantenha produtos de quantidade zero. Depois da
agregação, retenha receita >= `minimo_centavos`, que deve ser inteiro >= 0;
mínimo negativo ou cabeçalho sem coluna obrigatória também lança `ValueError`.
O domínio de entrada não inclui CSV com aspas quebradas ou colunas duplicadas.

Devolva a lista ordenada por produto (ordem padrão de strings Python), contendo
somente `produto`, `quantidade`, `receita_centavos` em cada dicionário. Grave essa
mesma lista em JSON UTF-8, preservando acentos sem escapes ASCII e com uma quebra
de linha final. A indentação é livre. Um CSV só com cabeçalho gera `[]`.
Valide tudo antes de criar/sobrescrever a saída; em `ValueError` a saída anterior
deve permanecer intacta. Erros de acesso a arquivos podem propagar normalmente.

Aceite também um BOM UTF-8 no início do arquivo. Nas células numéricas pagas,
após `strip()`, aceite apenas a gramática `[+-]?[0-9]+` (dígitos ASCII); zeros
à esquerda e sinal `+` são válidos, mas underscores, dígitos Unicode, decimais
e notação exponencial não são. O inteiro resultante deve ser >= 0. Mantenha
aritmética inteira exata, inclusive além de 64 bits. `minimo_centavos` precisa
ser exatamente `int` (qualquer outro tipo, como bool, float, str ou None, gera
`ValueError`, também sem alterar a saída). Linhas com campos faltando são
ignoradas se não pagas; se pagas, campos obrigatórios faltantes são inválidos.
Arquivo vazio não tem cabeçalho válido. Preserve quebras de linha e aspas
internas de produtos cotados; não normalize Unicode, caixa ou espaços internos.
Os testes podem ter 30.000 linhas.

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
