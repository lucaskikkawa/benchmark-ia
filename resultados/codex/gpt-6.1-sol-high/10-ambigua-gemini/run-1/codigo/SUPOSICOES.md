# Decisões e premissas

## Cálculo obrigatório

O score é calculado exatamente como `round(sum(compras) * 0.1 + anos_ativo * 5, 2)`.
A soma é feita sobre todas as compras, e somente o resultado final é arredondado.
Não há arredondamento individual de compras, bônus adicionais, teto ou piso de
pontuação. Uma lista vazia soma zero; nesse caso, apenas os anos ativos contribuem.

O arredondamento segue a função nativa `round` do Python, inclusive sua regra de
desempate para o número par e as particularidades da representação binária de
`float`. Não se usa arredondamento financeiro com `Decimal`, pois isso poderia
divergir da expressão exigida. Duas casas decimais referem-se ao arredondamento do
valor numérico, e não à apresentação: por exemplo, `10.0` não é convertido na
string `"10.00"`.

## Categorias e limites

As categorias são definidas pelo **score final já arredondado**:

| Categoria | Faixa de score |
| --- | --- |
| Bronze | score < 100 |
| Prata | 100 <= score < 500 |
| Ouro | 500 <= score < 1000 |
| Platina | score >= 1000 |

Os limites inferiores são inclusivos e os superiores exclusivos. Assim, 100
pontos recebem Prata, 500 recebem Ouro e 1000 recebem Platina. Zero e pontuações
negativas recebem Bronze. Um valor bruto de 99.999, arredondado para 100.0,
recebe Prata. Todas as entradas no domínio assumido recebem uma string não vazia.

Esses nomes e limites são uma convenção de negócio adotada na ausência de faixas
prescritas. As faixas são crescentes, não se sobrepõem e cobrem toda pontuação
finita, mantendo uma relação simples entre pontuação e nível. Não foi presumida
uma distribuição estatística de clientes nem um critério baseado em percentis.

## Valores negativos

- Compras negativas são tratadas como estornos ou devoluções e entram na soma
  com seu sinal original. Não são descartadas nem convertidas para valores
  absolutos. Por exemplo, compras de 200 e -50 contribuem com 15 pontos.
- Anos ativos negativos contribuem com cinco pontos negativos por ano. Embora
  possam indicar um problema nos dados de origem, não são ajustados para zero
  nem rejeitados: a fórmula obrigatória continua sendo aplicada literalmente.
- O score final pode ser negativo; não há limitação artificial a zero.

## Entrada, saída e preservação

Presume-se que os quatro campos obrigatórios estejam presentes, que `id` e
`nome` sejam strings, que `compras` seja uma lista de números `int` ou `float`
finitos e que `anos_ativo` seja inteiro. Os valores e resultados intermediários
devem ser representáveis pela aritmética numérica utilizada. Booleanos, strings
numéricas, `None`, NaN e infinitos não fazem parte do domínio assumido.

Não há uma camada adicional de validação ou conversão: entradas fora desse
contrato não têm comportamento garantido. Campos ausentes podem gerar
`KeyError`, e operações sobre tipos incompatíveis podem gerar `TypeError`.
Isso evita inventar valores padrão para informações obrigatórias ausentes.

O retorno é um novo dicionário contendo somente `id`, `nome`, `score` e
`categoria`. Campos adicionais da entrada são ignorados no cálculo e omitidos
do retorno; continuam intactos no dicionário original. O identificador e o nome
são copiados sem normalização, remoção de espaços, alteração de caixa ou
codificação manual, preservando caracteres Unicode, inclusive acentos e emojis.

A função apenas lê a entrada: não ordena, remove, acrescenta ou altera compras,
nem escreve no dicionário recebido. Não mantém estado global ou referências à
lista de compras no resultado. Chamadas sucessivas com os mesmos valores
produzem resultados iguais.

## Volume e custo

A soma percorre a lista uma única vez, em tempo O(n), com espaço auxiliar O(1)
em relação à quantidade de compras, sem criar uma segunda lista ou usar
recursão. A classificação e a construção do retorno têm custo constante.
Não há limite artificial para a quantidade de compras; os limites práticos são
os recursos disponíveis e a capacidade de representação numérica do Python.
