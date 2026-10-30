# Separar o cálculo de subtotais

Refatore `pedidos.py` sem alterar o comportamento de `resumo_pedidos(pedidos)`.
A entrada é um iterável de dicionários com `categoria` (str), `quantidade` e
`preco_centavos` (inteiros >= 0), e `desconto_percentual` opcional (inteiro de
0 a 100, padrão 0). Não precisa validar entradas fora desse domínio.

Crie a função pública:

```python
def subtotal(quantidade: int, preco_centavos: int, desconto_percentual: int = 0) -> int:
    ...
```

Ela calcula `quantidade * preco_centavos * (100 - desconto_percentual) // 100`,
com truncamento por linha, nunca por unidade ou apenas no total geral.
`resumo_pedidos` DEVE chamar `subtotal` uma vez por pedido, inclusive com quantidade
zero. Esta delegação faz parte da estrutura exigida e será verificada substituindo
a função em tempo de execução. Troque os nomes opacos por nomes descritivos.

O retorno segue `{'itens': soma_das_quantidades, 'total_centavos': soma_dos_subtotais,
'por_categoria': {categoria: soma_dos_subtotais_da_categoria}}`. Preserve categorias
exatamente, inclusive as que somam zero. Não altere a entrada. Entrada vazia
produz `{'itens': 0, 'total_centavos': 0, 'por_categoria': {}}`.

O iterável pode ser de passagem única. Faça as chamadas a `subtotal` na ordem
dos pedidos e use o valor devolvido pelo helper em ambas as agregações, mesmo
quando ele for substituído nos testes. Não agrupe linhas antes da delegação.
Inteiros têm precisão arbitrária, inclusive muito além de 64 bits; o cálculo
não pode perder centavos por conversão para float. Categorias não devem sofrer
strip, casefold ou normalização Unicode. Chamadas não compartilham acumuladores.

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
