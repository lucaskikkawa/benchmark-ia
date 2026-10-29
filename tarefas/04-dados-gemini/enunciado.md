# 04 - Processamento de Dados Financeiros (CSV e JSON)

Implemente a função `processar_vendas` no arquivo `analisador_vendas.py` na raiz do seu diretório de trabalho.

## Assinatura

```python
def processar_vendas(
    caminho_csv: str,
    caminho_json_saida: str,
    status_filtro: str = "concluido",
    top_n: int = 3,
) -> dict:
    ...
```

## Especificação

O arquivo CSV de entrada possui cabeçalho com os seguintes campos:
`id_transacao,data,cliente,categoria,valor,status`

### Comportamento:
1. **Validação de Parâmetros e Arquivos**:
   - Se `caminho_csv` não existir ou não for um arquivo, deve levantar `FileNotFoundError`.
   - Se `top_n < 1`, deve levantar `ValueError`.
2. **Leitura e Filtragem**:
   - Abra o arquivo com codificação UTF-8.
   - Filtre apenas as linhas onde o campo `status` seja igual a `status_filtro` (comparação case-insensitive e sem espaços em branco nas pontas, por exemplo `"Concluido "` é igual a `"concluido"`).
   - Ignore linhas com valores inválidos (não conversíveis para float, ou com valores negativos).
3. **Métricas Agregadas**:
   - `"total_transacoes"`: número inteiro de transações filtradas válidas.
   - `"receita_total"`: soma dos valores válidos filtrados, arredondada para 2 casas decimais (`float`).
   - `"ticket_medio"`: média (`receita_total / total_transacoes`) arredondada para 2 casas decimais. Se não houver transações, deve ser `0.0`.
   - `"por_categoria"`: dicionário `{categoria: total_gasto}` ordenado alfabeticamente pelo nome da categoria, com valores arredondados para 2 casas decimais.
   - `"top_clientes"`: lista com os `top_n` maiores compradores (ou todos, se o total de clientes distintos for menor que `top_n`).
     - Formato de cada item: `{"cliente": "Nome", "total": float}` (com total arredondado para 2 casas).
     - Ordenação: maior total primeiro (decrescente). Em caso de empate de total, desempate por ordem alfabética do nome do cliente (crescente).
4. **Escrita do JSON**:
   - Salve o dicionário resultante no caminho indicado por `caminho_json_saida` em formato JSON, formatado com `indent=2` e `ensure_ascii=False`.
5. **Retorno**:
   - Retorne o dicionário calculado.
