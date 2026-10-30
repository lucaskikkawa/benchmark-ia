# Suposições e Decisões de Design

Este documento registra as decisões tomadas para os pontos que a especificação
(`enunciado.md`) deixou em aberto. O núcleo explícito (cálculo do score, chaves
do retorno, imutabilidade e suporte a Unicode/grandes volumes) segue exatamente
o que foi especificado; tudo o que está descrito aqui é complemento.

## 1. Cálculo do score (núcleo explícito)

- `score = round(soma_compras * 0.1 + anos_ativo * 5, 2)`.
- A soma das compras usa `math.fsum`, que é exato o bastante para listas grandes
  e evita erro acumulado de ponto flutuante (ex.: `0.1 + 0.2 + ...`).
- O resultado é sempre `float`, mesmo quando todas as entradas são inteiras.

## 2. Categorias e faixas de pontuação

Foram definidas quatro categorias, com base no score final:

| Categoria  | Faixa de score (inclusiva) |
|------------|----------------------------|
| `Diamante` | score >= 300               |
| `Ouro`     | 150 <= score < 300         |
| `Prata`    | 50 <= score < 150          |
| `Bronze`   | score < 50                 |

Justificativa:
- Os limites são arbitrários, pois a especificação não os fornece. Estão
  centralizados em `FAIXAS_CATEGORIA` em `solucao.py`, para ajuste sem mexer na
  lógica.
- Um cliente com 10 anos de fidelidade e compras de R$ 0 já chega a 50 pontos
  (Prata); um cliente novo precisa de cerca de R$ 500 em compras para ser Prata.
  Assim, fidelidade e volume de compras têm pesos comparáveis.
- A categoria é derivada apenas do score final; não há regra separada por
  quantidade de compras ou por tempo.

## 3. Valores negativos na lista de compras

- **Decisão:** valores negativos são tratados como estornos/devoluções e entram
  na soma como estão, reduzindo o `soma_compras`.
- Alternativa descartada: ignorá-los. Ignorar um estorno inflaria o score de um
  cliente que devolveu produtos.
- Consequência: o score pode ficar negativo (ex.: compras totalizando -1000 e
  zero anos ativos). Nesse caso a categoria é `Bronze`, a menor faixa
  (`CATEGORIA_PADRAO`), e o score negativo é preservado no retorno, sem ser
  truncado, para não esconder a informação.

## 4. Anos ativos negativos

- **Decisão:** `anos_ativo < 0` é tratado como `0` (`max(anos_ativo, 0)`).
- Justificativa: não existe "tempo de fidelidade negativo". Um valor negativo
  provavelmente é erro de entrada; penalizar o cliente além do score de compras
  seria uma decisão de negócio não especificada. Tratar como zero é a opção
  conservadora.

## 5. Campos adicionais na entrada

- **Decisão:** campos extras no dicionário `dados` são ignorados.
- O retorno contém somente as chaves obrigatórias: `id`, `nome`, `score`,
  `categoria`.

## 6. Campos ausentes (robustez)

Não estavam na especificação, mas o código se comporta de forma definida:

- `compras` ausente: assume `[]` (score de compras = 0).
- `anos_ativo` ausente: assume `0`.
- `id` ou `nome` ausentes: geram `KeyError`. Esses campos são obrigatórios e
  não há um valor padrão razoável para identificar o cliente.

## 7. Imutabilidade

- A função apenas lê `dados` e `compras`; nenhuma atribuição é feita sobre a
  entrada.
- O retorno é um dicionário novo. Os valores `id` e `nome` são repassados como
  referência (strings são imutáveis em Python, então não há risco de mutação).

## 8. Unicode e grande volume

- `id` e `nome` são repassados sem normalização, preservando exatamente os
  caracteres de entrada (acentos, emojis, etc.). Não há `strip`, `lower` ou
  normalização Unicode, porque isso alteraria o valor "preservado".
- `math.fsum` e a iteração simples sobre a lista operam em tempo linear e
  memória constante em relação ao número de compras.

## 9. Tipos aceitos

- `compras` aceita `int` e `float`, conforme a especificação. Não há validação
  explícita de tipo; valores não numéricos levantam `TypeError` naturalmente
  durante a soma.
- `anos_ativo` é assumido como `int`. Um `float` funciona, mas é repassado à
  multiplicação sem conversão.

## 10. Arredondamento

- O arredondamento é feito somente no final (`round(..., 2)`), não nas
  parcelas intermediárias, para que o erro de arredondamento não se acumule.
