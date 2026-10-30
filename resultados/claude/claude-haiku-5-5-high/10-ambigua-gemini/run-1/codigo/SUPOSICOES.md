# Suposições e decisões de design

Este documento registra as decisões tomadas para os pontos que a especificação
deixou em aberto. O núcleo explícito (fórmula do score, chaves do retorno,
imutabilidade e suporte a Unicode) é implementado exatamente como descrito;
tudo o que está abaixo é complemento.

## 1. Fórmula do score (núcleo explícito)

```
score = round(sum(compras) * 0.1 + anos_ativo * 5, 2)
```

- A soma é feita com `sum()` sobre a lista original, sem `math.fsum`, para
  reproduzir exatamente a expressão da especificação (`soma_compras * 0.1`).
- O arredondamento é aplicado ao score final, uma única vez.
- O retorno usa `float` (o `* 0.1` sempre produz float).

## 2. Categorias e faixas de pontuação

Foram definidas quatro categorias, com limites inferiores **inclusivos**
aplicados sobre o score já arredondado:

| Categoria  | Faixa de score          |
|------------|-------------------------|
| `Platina`  | score ≥ 600             |
| `Ouro`     | 300 ≤ score < 600       |
| `Prata`    | 100 ≤ score < 300       |
| `Bronze`   | score < 100 (inclui negativos) |

Critérios que justificam essas faixas:

- **Escala da fórmula.** Um cliente que gasta R$ 1.000 no total e está ativo
  há um ano tem score 105, ou seja, já cai em `Prata`. Um cliente com R$ 5.000
  de compras e 5 anos ativos tem score 525 (`Ouro`). `Platina` exige score ≥ 600,
  o que ocorre com R$ 6.000 em compras e zero anos, ou com R$ 5.000 em compras e
  20 anos ativos (500 + 100). Isso separa os níveis sem tornar `Platina`
  inalcançável.
- **Degraus crescentes.** Os limites (100, 300, 600) crescem em degraus
  diferentes, sem uma progressão simétrica. São pontos de partida escolhidos por
  julgamento, não derivados de dados reais; devem ser recalibrados com a base de
  clientes.
- **Arredondamento antes de categorizar.** A categoria é calculada sobre o
  `score` já arredondado a 2 casas. Assim, o `score` retornado e a `categoria`
  são sempre consistentes entre si: não existe caso em que o score exibido seja
  `100.00` e a categoria seja `Bronze` por causa de um valor como `99.9999`.
- **Nomes.** Os nomes são strings em português, não vazias, com a primeira
  letra maiúscula, para uso direto em relatórios.

Os limites estão em uma única constante (`CATEGORIAS`, no topo de
`solucao.py`), ordenada do maior para o menor. Ajustar as faixas exige alterar
apenas essa tupla.

## 3. Valores negativos na lista de compras (estornos/devoluções)

**Decisão: estornos são somados como valores negativos**, ou seja, reduzem o
score base. Não são ignorados.

Justificativas:

- A regra explícita é "10% da soma dos valores das compras". Um estorno é um
  valor de compra com sinal negativo; excluí-lo alteraria a fórmula sem
  respaldo na especificação.
- Um cliente que devolveu parte do que comprou gastou, de fato, menos. Tratar
  o estorno como neutro superestimaria a fidelidade.
- Não há clamp no score base. Um cliente cujos estornos superem as compras pode
  ter score base negativo. Isso é intencional e reflete o saldo líquido.

Consequências:

- Um score final negativo é possível (ex.: `compras = [-500]`, `anos_ativo = 0`
  gera `score = -50.0`). Nesse caso a categoria é `Bronze`, por ser a menor
  faixa, que inclui qualquer valor abaixo de 100.
- Não há validação de tipo nos valores de `compras`. Valores não numéricos
  (ex.: `None` ou string) geram `TypeError` do próprio Python ao somar.

## 4. Anos ativos negativos

**Decisão: `anos_ativo` negativo é ajustado para 0** (`max(anos_ativo, 0)`).

Justificativas:

- Um tempo de atividade negativo não tem significado. A alternativa de lançar
  exceção quebraria o contrato de retorno da função, que deve sempre devolver o
  dicionário com as quatro chaves.
- Ajustar para 0 significa que o cliente não recebe pontos de fidelidade, mas
  continua classificado com base nas compras. Isso é o comportamento mais
  conservador: nenhum bônus é concedido por dado inválido.

Ainda assim, o score de fidelidade é calculado sobre o valor ajustado. Não há
registro de que o dado original estava errado; se isso importar para o negócio,
a validação deve ocorrer na origem dos dados.

## 5. Campos adicionais na entrada

**Decisão: campos extras são ignorados e não aparecem no retorno.**

- O retorno contém exatamente `id`, `nome`, `score` e `categoria`, como exige a
  especificação. Copiar campos extras poderia expor dados que o chamador não
  esperava compartilhar, e tornaria o formato de saída dependente da entrada.
- Campos extras não afetam o cálculo.

## 6. Campos ausentes ou nulos

Além dos casos da especificação, foi adotado um comportamento tolerante para
dois campos de cálculo:

- `compras` ausente ou `None` é tratada como lista vazia (score base 0).
- `anos_ativo` ausente ou `None` é tratado como 0.

Já `id` e `nome` são obrigatórios. Se estiverem ausentes, a função lança
`KeyError`. Não há valor padrão razoável para identificar um cliente, e
inventar um id poderia misturar registros diferentes.

## 7. Imutabilidade

- A função nunca atribui nada sobre `dados` nem sobre a lista `compras`. Usa
  apenas leitura (`get`, `sum`).
- Os valores de `id` e `nome` são repassados como o mesmo objeto recebido, o que
  preserva a identidade e o conteúdo.

## 8. Volume e Unicode

- O cálculo usa `sum()` em uma única passagem, sem criar cópias da lista, então
  listas grandes são processadas em tempo linear e com memória constante.
- `id` e `nome` não são manipulados, apenas repassados. Strings Unicode (acentos,
  emojis, caracteres de escrita não latina) são preservadas sem transformação.

## 9. Premissas gerais

- Os valores monetários estão todos na mesma moeda e na mesma unidade. A
  função não faz conversão.
- `anos_ativo` é um número inteiro de anos, como indicado pela especificação.
  Valores fracionários seriam aceitos pelo cálculo, mas não são o caso esperado.
- A função é pura em relação aos seus argumentos: mesma entrada, mesma saída, sem
  efeitos colaterais, sem acesso a rede ou disco.
