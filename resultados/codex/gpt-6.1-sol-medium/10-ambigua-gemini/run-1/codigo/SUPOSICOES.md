# Suposições e decisões de design

## Cálculo obrigatório

O score é calculado exatamente como `round(sum(compras) * 0.1 + anos_ativo * 5, 2)`.
O arredondamento ocorre uma única vez, após somar os dois componentes. Não se
arredondam compras individuais nem componentes intermediários. Uma lista vazia
tem soma zero; nesse caso, apenas os anos ativos contribuem para o score.

Usa-se o `round` nativo do Python, inclusive seu comportamento de desempate para
o número par e as limitações da representação binária de ponto flutuante.
Não se aplica arredondamento financeiro alternativo. O retorno é numérico, sem
formatação textual ou garantia de exibir zeros finais.

## Categorias

Como não foram fornecidas faixas comerciais, foram escolhidos quatro níveis
simples e determinísticos. Os limites são decisões desta implementação, passíveis
de revisão caso surjam regras de negócio:

| Categoria | Intervalo do score final |
| --- | --- |
| Bronze | score < 100 |
| Prata | 100 <= score < 500 |
| Ouro | 500 <= score < 1000 |
| Diamante | score >= 1000 |

A classificação utiliza o score **já arredondado**, exatamente como retornado.
Assim, um valor bruto que arredonde para 100 pertence a Prata. Os limites inferiores
de Prata, Ouro e Diamante são inclusivos; não há lacunas nem sobreposição.
Scores negativos e zero pertencem a Bronze. Não há teto para Diamante.
Os nomes são rótulos de segmentação, sem implicar benefícios ou descontos.

## Valores negativos

Compras negativas são interpretadas como estornos ou devoluções e participam
integralmente da soma. Não são descartadas, convertidas para valores absolutos
nem limitadas a zero. Isso preserva a fórmula obrigatória mesmo quando o total
líquido de compras é negativo.

Anos ativos negativos são mantidos no cálculo e contribuem com cinco pontos
negativos por ano. Embora possam representar inconsistência cadastral, ajustá-los
silenciosamente alteraria a fórmula explícita. Uma eventual validação cadastral
deve ocorrer antes da chamada. O score final também não é limitado a zero.

## Contrato de entrada e campos adicionais

Espera-se um dicionário com todas as quatro chaves obrigatórias e os tipos
descritos no enunciado: `id` e `nome` como strings, `compras` como lista de números
e `anos_ativo` como inteiro. Os números devem ser finitos, e os cálculos devem
caber na representação numérica do Python. Não há conversão automática de strings,
preenchimento de campos ausentes ou validação específica de tipos fora do contrato.
Nesses casos, as exceções naturais das operações do Python podem ser propagadas;
não se promete uma mensagem de erro específica.

Campos adicionais são ignorados e não aparecem no resultado. O retorno contém
exatamente `id`, `nome`, `score` e `categoria`. Identificadores e nomes são
preservados sem normalização Unicode, remoção de espaços ou mudança de caixa;
nenhuma restrição de caracteres ou de string não vazia é acrescentada.

## Imutabilidade e volume

A função cria um novo dicionário de retorno e apenas lê a entrada. Não ordena,
substitui ou edita a lista de compras, nem adiciona ou remove campos de `dados`.
Como os campos preservados são strings imutáveis, não é necessário copiá-los.
Chamadas repetidas com os mesmos dados produzem resultados iguais, sem estado
global ou efeitos colaterais.

A soma percorre a lista uma única vez: tempo O(n), com n igual ao número de
compras, e memória auxiliar O(1), sem criar outra lista. Essa escolha permite
históricos grandes, sujeitos à memória disponível para a própria entrada e aos
limites usuais de precisão de ponto flutuante.
