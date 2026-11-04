# Suposições e Decisões de Design — `classificar_cliente`

Este documento registra as decisões tomadas para os pontos que a especificação
deixou em aberto. O núcleo explícito (fórmula do score, chaves de retorno,
imutabilidade, suporte a Unicode e a grandes volumes) foi seguido literalmente.

## 1. Fórmula do score (núcleo, sem alteração)

```
score = round(soma(compras) * 0.1 + anos_ativo_efetivo * 5, 2)
```

- O arredondamento é feito **uma única vez**, sobre o total, como pede a regra 3
  (não se arredondam as parcelas separadamente).
- A soma usa o `sum()` nativo, que é exatamente a operação descrita
  (`soma_compras`). Não foi usado `math.fsum` para que o resultado coincida
  bit a bit com a fórmula de referência `round(sum(compras) * 0.1 + anos * 5, 2)`.
- O tipo de `score` é o retornado por `round(..., 2)`: `float` quando há
  compras em ponto flutuante, `int`/`float` conforme a aritmética do Python.
  A especificação aceita ambos.

## 2. Categorias e faixas

A categoria é derivada **apenas do score final** (já arredondado), para que
seja reproduzível a partir da saída da própria função.

| Categoria  | Faixa de score            |
|------------|---------------------------|
| `Bronze`   | `score < 100` (inclui 0 e negativos) |
| `Prata`    | `100 <= score < 500`      |
| `Ouro`     | `500 <= score < 1000`     |
| `Diamante` | `score >= 1000`           |

Justificativa:
- Nomes de metais/pedras são uma convenção amplamente reconhecida em programas
  de fidelidade e deixam a ordem hierárquica evidente.
- Limites inferiores são **inclusivos** (`>=`), evitando ambiguidade nas
  fronteiras (ex.: score exatamente 100 → `Prata`).
- As faixas crescem aproximadamente em escala (100 / 500 / 1000). Como referência:
  um cliente com 10 anos de casa (50 pts) precisa de ~R$ 500 em compras para
  chegar a `Prata`, ~R$ 4.500 para `Ouro` e ~R$ 9.500 para `Diamante`.
- `Bronze` é a categoria mínima garantida, de modo que `categoria` **nunca é
  vazia**, mesmo para clientes novos, sem compras ou com saldo negativo.
- As faixas ficam centralizadas na constante `FAIXAS_CATEGORIA` em
  `solucao.py`, facilitando ajuste pelo negócio sem tocar na lógica.

## 3. Valores negativos em `compras`

**Decisão:** valores negativos são interpretados como **estornos/devoluções** e
entram normalmente na soma, abatendo o total.

- Isso respeita literalmente a regra 1 ("10% da soma dos valores das compras").
- Ignorar negativos permitiria que um cliente comprasse e devolvesse para
  inflar artificialmente o score; abater é mais justo e mais resistente a abuso.
- Consequência: o score pode ficar negativo se as devoluções superarem as
  compras somadas aos pontos de fidelidade. Nesse caso o score é **retornado
  negativo, sem truncamento**, para preservar a informação (é sinal de algo a
  investigar), e a categoria atribuída é `Bronze`.
- Valores `0` são aceitos e não alteram o score.

## 4. `anos_ativo` negativo

**Decisão:** anos ativos negativos não têm significado de negócio e são
tratados como erro de dado benigno: aplica-se `max(anos_ativo, 0)`, ou seja,
contribuem com **0 pontos** de fidelidade (não penalizam o cliente).

- Optou-se por normalizar em vez de lançar exceção para não interromper o
  processamento em lote de muitos clientes por causa de um campo mal
  preenchido.
- Para `anos_ativo >= 0` a fórmula é exatamente a da especificação.

## 5. Campos adicionais na entrada

**Decisão:** campos extras (ex.: `email`, `cidade`) são **ignorados** e **não**
são copiados para a saída.

- A saída contém exatamente `id`, `nome`, `score` e `categoria` — um contrato
  estável e previsível, que também evita vazar dados não solicitados
  (ex.: dados pessoais) para quem consome o resultado.
- Campos extras não causam erro.

## 6. Validação de entrada

Entradas estruturalmente inválidas geram exceção (falha rápida), pois não há
forma segura de calcular um score a partir delas:

| Situação                                         | Exceção      |
|--------------------------------------------------|--------------|
| `dados` não é `dict`                             | `TypeError`  |
| Falta `id`, `nome`, `compras` ou `anos_ativo`    | `KeyError`   |
| `id` ou `nome` não são `str`                     | `TypeError`  |
| `compras` não é lista/tupla                      | `TypeError`  |
| Item de `compras` não numérico (ou `bool`)       | `TypeError`  |
| Item de `compras` `NaN` ou infinito              | `ValueError` |
| `anos_ativo` não é `int` (ou é `bool`)           | `TypeError`  |

- `bool` é rejeitado explicitamente porque em Python é subclasse de `int`,
  e `True` como valor de compra ou ano quase certamente é um erro.
- `compras` vazia é válida (soma = 0).
- `id` e `nome` vazios são aceitos: a especificação só exige que sejam
  preservados.

## 7. Imutabilidade

- A função apenas **lê** `dados` e `dados["compras"]`; não há atribuição,
  `append`, `sort` ou qualquer outra operação mutável sobre eles.
- O dicionário de retorno é um objeto novo. `id` e `nome` são `str`
  (imutáveis), portanto compartilhá-los com a entrada é seguro.

## 8. Unicode e grande volume

- `id` e `nome` são repassados sem normalização, `strip` ou mudança de
  caixa — preservação exata, incluindo acentos, emojis, CJK etc.
- O cálculo é O(n) em tempo e O(1) em memória adicional (sem cópias da
  lista), adequado para históricos com milhões de compras.
