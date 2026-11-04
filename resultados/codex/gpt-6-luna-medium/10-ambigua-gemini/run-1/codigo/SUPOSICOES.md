# Suposições de design

A especificação determina a fórmula do score e os campos obrigatórios do retorno, mas deixa algumas decisões de produto em aberto. Este documento registra as convenções adotadas pela implementação.

## Cálculo

- O score de compras é 10% da soma algébrica de todos os valores em `compras`. Assim, valores negativos são tratados como estornos ou devoluções e reduzem o total, em vez de serem descartados ou convertidos em valor absoluto.
- O score de fidelidade é cinco pontos por ano ativo. Como tempo ativo negativo não faz sentido como duração, `anos_ativo` abaixo de zero é tratado como zero antes do cálculo.
- O score final é a soma das duas parcelas e é arredondado com `round(..., 2)`, conforme a regra explícita. Não há arredondamentos intermediários.
- A implementação espera que os campos obrigatórios existam e que os valores de compras e anos ativos sejam numéricos e compatíveis com a operação. Validação e coerção de tipos não foram especificadas, então erros de entrada inválida são deixados para o comportamento normal do Python.

## Categorias

As categorias são determinadas pelo score final já arredondado, usando limites inclusivos no início de cada faixa:

| Score | Categoria |
|---|---|
| menor que 100 | Bronze |
| de 100 (inclusive) a menos de 500 | Prata |
| de 500 (inclusive) a menos de 1000 | Ouro |
| 1000 ou mais | Platina |

As faixas são simples, crescentes e não sobrepostas. Scores negativos ficam em Bronze, o nível inicial, inclusive quando o efeito líquido de estornos for negativo. Os nomes são rótulos de segmento e não alteram o score.

## Campos e imutabilidade

- O retorno inclui somente `id`, `nome`, `score` e `categoria`, os quatro campos definidos como obrigatórios. Campos adicionais de entrada são ignorados, sem serem copiados ou transformados.
- `id` e `nome` são repassados sem normalização, preservando inclusive caracteres Unicode.
- A lista de compras é percorrida por `sum` e não é modificada; o dicionário de entrada também é apenas consultado. Portanto, a chamada não altera a entrada.
- `sum` percorre a lista em tempo linear e não cria uma cópia dela, o que mantém o processamento adequado para históricos extensos.
