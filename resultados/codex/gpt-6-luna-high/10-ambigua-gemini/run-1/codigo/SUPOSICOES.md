# Suposições de design

Este documento registra as decisões adotadas para os aspectos que o enunciado
deixa em aberto. As fórmulas do núcleo explícito são aplicadas sem alterações:
o score de compras é `sum(compras) * 0.1`, a fidelidade é `anos_ativo * 5`, e o
score final é a soma dos dois arredondada com `round(..., 2)`.

## Categorias e faixas

As categorias são determinadas pelo score final, já arredondado, para que a
classificação corresponda ao número exibido e retornado:

| Score final | Categoria |
| --- | --- |
| Menor que 100 | Bronze |
| De 100 até menos que 500 | Prata |
| De 500 até menos que 1.000 | Ouro |
| 1.000 ou mais | Platina |

As faixas são inclusivas no limite inferior e exclusivas no limite superior.
Scores negativos permanecem na categoria Bronze. Os nomes são rótulos
qualitativos simples e sempre formam uma string não vazia.

## Valores negativos em compras

Valores negativos são considerados parte do histórico e entram diretamente na
soma. Assim, um estorno ou devolução reduz o total de compras e, portanto, o
score de compras. Não se converte valor negativo em zero nem se elimina esse
registro: o enunciado define a parcela de compras a partir da soma dos valores,
e interpretar valores negativos como ajustes é uma convenção coerente com essa
fórmula.

## Anos ativos negativos

`anos_ativo` é usado como recebido, inclusive se negativo, seguindo a fórmula
explícita `anos_ativo * 5`. Portanto, um valor negativo diminui o score de
fidelidade. Não há normalização para zero nem validação adicional, pois o
enunciado não define um comportamento alternativo e a fórmula especificada é
direta.

## Campos adicionais e imutabilidade

Campos além de `id`, `nome`, `compras` e `anos_ativo` são ignorados; o retorno
contém somente as quatro chaves obrigatórias. `id` e `nome` são copiados para
as respectivas chaves do novo dicionário sem transformação, preservando seu
valor (inclusive caracteres Unicode). As compras são apenas percorridas por
`sum`; nem o dicionário de entrada nem a lista são alterados. O algoritmo
percorre as compras uma vez, com tempo linear e memória auxiliar constante,
suportando históricos grandes.

## Entradas consideradas

Assume-se que os campos obrigatórios estão presentes e que compras e anos
ativos contêm valores numéricos compatíveis com os tipos descritos no
enunciado. Entradas ausentes ou tipos incompatíveis estão fora do contrato e
não recebem tratamento especial.
