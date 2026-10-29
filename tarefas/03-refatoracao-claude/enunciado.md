# Tarefa: refatorar `relatorio.py` sem mudar o comportamento

O arquivo `relatorio.py` (no diretório de trabalho) contém `gerar_relatorio(pedidos)`, que funciona,
mas é difícil de ler e manter. **Refatore `relatorio.py`** mantendo exatamente o mesmo comportamento
observável de `gerar_relatorio` (mesma string retornada, mesmas exceções) para qualquer entrada.

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

As taxas devem ficar definidas em um único lugar (ex.: uma constante do módulo), não espalhadas em if/elif.
Use apenas a biblioteca padrão e não crie outros arquivos obrigatórios.
