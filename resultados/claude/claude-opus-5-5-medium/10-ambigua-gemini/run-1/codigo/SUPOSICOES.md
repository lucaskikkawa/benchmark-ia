# Suposições e Decisões de Design — `classificar_cliente`

## Núcleo (seguido literalmente)
- `score = round(soma(compras) * 0.1 + anos_ativo * 5, 2)`.
- O retorno é um **novo** dicionário com exatamente as chaves `id`, `nome`, `score` e `categoria`.
- `id` e `nome` são devolvidos como recebidos (sem normalização, `strip`, `lower` etc.), preservando qualquer caractere Unicode.
- A entrada nunca é modificada: a função só lê `dados` e `compras` (`sum` não altera a lista; nenhuma ordenação/filtragem in-place).
- Grande volume: o cálculo é O(n) em uma única passada de validação + `sum`, sem cópias da lista.

## Categorias
Critério baseado exclusivamente no **score final** (que já combina gasto e fidelidade):

| Categoria  | Faixa de score            |
|------------|---------------------------|
| `Diamante` | score ≥ 1000              |
| `Ouro`     | 500 ≤ score < 1000        |
| `Prata`    | 100 ≤ score < 500         |
| `Bronze`   | score < 100 (inclui score 0 e negativo) |

- Limites inferiores são inclusivos (ex.: score exatamente 500,00 → `Ouro`).
- A comparação é feita sobre o score já arredondado, para que a categoria seja coerente com o score exibido.
- Clientes sem compras e sem tempo de casa ficam em `Bronze` — a categoria nunca é vazia.
- As faixas estão centralizadas na constante `FAIXAS_CATEGORIA`, facilitando ajuste pelo negócio.
- Referência intuitiva: `Prata` ≈ R$ 1.000 em compras (ou 20 anos de casa); `Ouro` ≈ R$ 5.000; `Diamante` ≈ R$ 10.000.

## Compras com valores negativos
- Interpretados como **estornos/devoluções**: entram na soma e abatem o total (soma líquida). Isso segue a regra literal "10% da soma dos valores das compras" e evita que um cliente ganhe pontos por uma compra que foi devolvida.
- Consequência: se os estornos superarem as compras, o score base pode ficar negativo e o score final pode ser negativo; nesse caso a categoria é `Bronze`. Optei por não "zerar" o score para não divergir da fórmula explícita.
- Valores `0` são aceitos e não alteram o score.

## Anos ativos negativos
- Não têm significado de negócio (provável erro de cadastro); são tratados como **0** (`max(anos_ativo, 0)`), ou seja, não penalizam o cliente nem geram pontos.
- Valores não inteiros (ex.: `2.5`) são aceitos e calculados proporcionalmente (`2.5 * 5 = 12.5`).

## Campos ausentes, adicionais e tipos
- **Campos adicionais** na entrada (ex.: `email`, `cidade`) são **ignorados** e não são copiados para a saída, mantendo o contrato de retorno enxuto e previsível.
- `compras` ausente ou `None` → lista vazia (score base 0). `anos_ativo` ausente ou `None` → 0.
- `id`/`nome` ausentes → `None` no retorno (a função não inventa valores).
- Validação de tipos (`TypeError`):
  - `dados` que não seja `dict`;
  - `compras` que não seja lista/tupla;
  - qualquer valor de compra ou `anos_ativo` não numérico (strings, `None` dentro da lista, etc.).
  - `bool` é rejeitado explicitamente, pois embora seja subclasse de `int` em Python, `True` não representa um valor monetário.
- Preferi falhar explicitamente a ignorar silenciosamente dados corrompidos, que distorceriam o score.

## Precisão numérica
- Usa-se `sum()` nativo seguido de `round(..., 2)`, exatamente como especificado. Para listas muito grandes, erros de ponto flutuante acumulados são da ordem de 1e-10 e desaparecem no arredondamento para 2 casas.
- O score retornado é sempre `float` (a multiplicação por `0.1` já produz float), o que é aceito pela especificação.
