# Tarefa: refatorar `relatorio.py` sem mudar o comportamento

O arquivo `relatorio.py` (no diretório de trabalho) contém `gerar_relatorio(pedidos)`, que funciona,
mas é difícil de ler e manter. **Refatore `relatorio.py`** mantendo exatamente o mesmo comportamento
observável de `gerar_relatorio` (mesma string retornada, caractere a caractere, e mesmo tipo de exceção)
para qualquer entrada — inclusive valores `float` "difíceis" (arredondamento na 2ª casa, valores
enormes, `inf`/`nan`), tipos de cliente desconhecidos e pedidos/itens malformados (chaves ausentes).
A lista `pedidos` e os dicts aninhados não são modificados.
Os testes comparam a sua versão com a original em muitas entradas.

## Entrada

`pedidos` é uma lista de dicts no formato:

```python
{"cliente": "Ana", "tipo": "vip", "itens": [{"preco": 10.0, "qtd": 2}, ...]}
```

## Estrutura exigida

Além de `gerar_relatorio(pedidos: list[dict]) -> str`, o módulo deve expor estas funções públicas
(`gerar_relatorio` deve usá-las, buscando-as no escopo do módulo, sem duplicar a lógica):

```python
def calcular_subtotal(itens: list[dict]) -> float:
    """Soma preco * qtd dos itens. ValueError se algum qtd < 0. Lista vazia -> 0."""

def calcular_desconto(subtotal: float, tipo_cliente: str) -> float:
    """Retorna o VALOR do desconto (não o total líquido) para o subtotal e o tipo de cliente."""

def formatar_relatorio(totais_por_cliente: dict[str, float]) -> str:
    """Gera o texto do relatório a partir do total líquido por cliente."""
```

Regras atuais (que devem ser preservadas) para o desconto, em função do tipo do cliente e de o subtotal
ser **maior que 1000** (exatamente 1000 usa a taxa da coluna "até 1000"):

| tipo | até 1000 | acima de 1000 |
|---|---|---|
| `vip` | 10% | 15% |
| `atacado` | 5% | 8% |
| qualquer outro | 0% | 2% |

As taxas devem ficar definidas em um único lugar, nestas constantes do módulo (não espalhadas em if/elif):

```python
LIMITE_FAIXA_ALTA = 1000
TAXAS_DESCONTO: dict[str, tuple[float, float]]  # tipo -> (taxa até o limite, taxa acima): "vip" e "atacado"
TAXAS_PADRAO: tuple[float, float]               # (taxa até o limite, taxa acima) dos demais tipos
```

`calcular_desconto` deve consultar essas constantes no momento da chamada (alterar
`relatorio.TAXAS_DESCONTO`, `relatorio.TAXAS_PADRAO` ou `relatorio.LIMITE_FAIXA_ALTA` muda o resultado).
O tipo do cliente é comparado exatamente (`"VIP"` não é `"vip"`).
Use apenas a biblioteca padrão e não crie outros arquivos obrigatórios.
