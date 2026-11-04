# Suposições — classificação de clientes

Este documento fecha os pontos que a especificação deixou em aberto e registra as premissas usadas por `classificar_cliente` em `solucao.py`. O cálculo do score segue as regras inequívocas; as escolhas abaixo só cobrem o que a especificação não fixou.

## Contrato de entrada e saída

A função espera um dicionário com as chaves obrigatórias `id` (str), `nome` (str), `compras` (sequência de `int` ou `float`) e `anos_ativo` (número, em geral `int`). O retorno tem exatamente quatro chaves, nesta ordem: `id`, `nome`, `score`, `categoria`.

Não são acrescentados campos intermediários (`soma_compras`, `score_compras`, `score_fidelidade`). A especificação exige a presença daquelas quatro chaves e não pede outras. Um retorno mínimo evita que um teste de igualdade do dicionário quebre por causa de chaves extras e mantém o contrato estável.

`id` e `nome` são repassados sem normalização, recorte, case-fold ou codificação. Dois identificadores que diferem só por espaço, acento ou caixa permanecem diferentes.

## Cálculo do score (núcleo fechado)

Ordem das operações:

1. `soma_compras = sum(compras)` — soma aritmética de todos os valores, na ordem da lista.
2. `score_compras = soma_compras * 0.1`.
3. `score_fidelidade = anos_ativo * 5`.
4. `score = round(score_compras + score_fidelidade, 2)`.
5. A categoria é decidida sobre esse `score` já arredondado.

A categoria usa o valor arredondado, não o valor bruto anterior ao `round`. Assim o número devolvido em `score` e o segmento em `categoria` não se contradizem. Exemplo: uma soma que produziria 49,996 antes do arredondamento vira `score` 50,00 e categoria `Prata`, não `Bronze`.

O arredondamento é o `round` nativo do Python 3 (half to even, o chamado arredondamento do banqueiro) para duas casas decimais, como a especificação pede. Não há arredondamento comercial “sempre para cima” em .5. Exemplos: `round(1.225, 2)` pode não ser 1,23 por causa da representação binária; o que vale é o resultado de `round` depois da soma em float. Não convertemos os valores para centavos inteiros nem para `decimal.Decimal`.

`score` é `float` nos casos previstos (a multiplicação por `0.1` promove a soma a float, inclusive quando a lista de compras está vazia, pois `0 * 0.1 == 0.0`).

## Compras negativas (estornos)

**Decisão:** todo número da lista entra na soma, inclusive zero e valores negativos.

**Por quê:** a regra fechada fala em “10% da soma dos valores das compras”, sem filtro de sinal. Um valor negativo é um estorno ou uma devolução que reduz o faturamento líquido do cliente. Ignorar negativos inflaria o score; tomar o módulo transformaria devolução em compra. As duas alternativas foram rejeitadas.

Consequências:

- Lista vazia: soma 0. Cliente sem compras não é erro.
- Zero é compra nula e não muda a soma.
- Se a soma for negativa, o score de compras é negativo e pode levar o score final a negativo, mesmo com anos ativos positivos.
- A lista não é ordenada, filtrada nem copiada. A soma percorre a sequência uma vez.

Premissa de tipo: cada item é `int` ou `float`, como na assinatura. `bool` é tecnicamente `int` em Python (`True == 1`), mas não é um valor de compra esperado; se aparecer, entra na soma como 1 ou 0. Valores não numéricos (`None`, `str`) não são tratados: `sum` levanta `TypeError`. Não há sentinela silenciosa.

## Anos ativos negativos ou nulos

**Decisão:** a fórmula `anos_ativo * 5` é aplicada literalmente, também quando `anos_ativo` é zero ou negativo. Não há corte para zero, valor absoluto nem rejeição da entrada.

**Por quê:** a concessão de 5 pontos por ano está na seção de regras inequívocas. O ponto em aberto pede uma interpretação, e a interpretação adotada é não corrigir o dado na função de classificação. Um ano negativo é anomalia de origem (campo ausente gravado como −1, erro de carga, cliente ainda não ativado com sentinela). Corrigir aqui esconderia o problema e desviaria da fórmula que a suíte do núcleo pode recalcular. O efeito no score é linear: cada ano negativo tira 5 pontos.

**Alternativa rejeitada:** `max(0, anos_ativo)`. Seria razoável num programa de fidelidade (não existe “tempo ativo negativo”), mas alteraria um produto que a especificação escreveu de forma fechada. Fica documentada como alternativa consciente, não como comportamento implementado.

Zero anos é um cliente novo ou inativo em tempo: contribui 0 ao score de fidelidade e é um caso normal, não um erro.

Anos não inteiros, se ocorrerem, também entram na multiplicação (`2.5 * 5 = 12.5`). A especificação declara `int`; a função não trunca. Anos não numéricos levantam `TypeError` na multiplicação.

## Categorias e faixas

A categoria é uma função somente do `score` arredondado. Não depende do nome, do volume de pedidos nem de uma combinação separada de compras e anos: esses fatores já estão condensados no score. Faixas fechadas à esquerda e abertas à direita, exceto `Crítico`, que é o semieixo negativo.

| Categoria | Score arredondado | Leitura de negócio |
| --- | --- | --- |
| `Crítico` | `< 0` | Estornos e/ou anos negativos superam o histórico positivo. Exige revisão cadastral, não benefício. |
| `Bronze` | `0 <= score < 50` | Cliente novo ou de baixo movimento. Cerca de até R$ 500 líquidos sem anos, ou poucos anos com pouca compra. |
| `Prata` | `50 <= score < 200` | Relacionamento estabelecido. Ex.: R$ 1.000 em compras (100 pontos) ainda sem década longa de casa, ou R$ 500 mais 10 anos (50 + 50). |
| `Ouro` | `200 <= score < 1000` | Alto valor. Ex.: R$ 2.000 líquidos (200 pontos) ou R$ 1.500 mais 10 anos (150 + 50). |
| `Platina` | `score >= 1000` | Topo da base. Ex.: R$ 10.000 líquidos, ou R$ 8.000 mais 40 anos (800 + 200). |

Os limiares 50, 200 e 1000 estão na escala do próprio score (10% do faturamento mais 5 pontos por ano), não em reais. Foram escolhidos para que:

- uma compra isolada pequena (dezenas de reais) caia em `Bronze`;
- um cliente com algumas centenas a poucos milhares de reais, ou vários anos de casa, chegue a `Prata` e `Ouro` sem precisar de uma vida inteira de cadastro;
- `Platina` fique restrito a faturamento realmente alto (ordem de R$ 10.000 líquidos, ou um pouco menos se a permanência for muito longa).

`score == 0` é `Bronze`, não `Crítico`. Zero descreve ausência de movimento (lista vazia e zero anos, ou compras e penalidades que se anulam). Score negativo descreve saldo desfavorável e fica isolado em `Crítico` para não misturar “ainda não comprou” com “devolveu mais do que comprou”.

Nomes em português, com acento em `Crítico`, estáveis e não vazios. Não há categoria `Novo`, `Inativo` ou `VIP`: “novo” e “inativo” já aparecem como `Bronze` quando o score é baixo, e o topo é `Platina`.

### Exemplos de fronteira

| Entrada resumida | Score | Categoria |
| --- | --- | --- |
| compras `[]`, anos `0` | `0.0` | `Bronze` |
| compras `[499.94]`, anos `0` | `49.99` | `Bronze` |
| compras `[500]`, anos `0` | `50.0` | `Prata` |
| compras `[2000]`, anos `0` | `200.0` | `Ouro` |
| compras `[10000]`, anos `0` | `1000.0` | `Platina` |
| compras `[80, -30]`, anos `2` | `15.0` | `Bronze` |
| compras `[-200]`, anos `1` | `-15.0` | `Crítico` |
| compras `[1000]`, anos `-3` | `85.0` | `Prata` |
| compras `[100, 50.5, 20]`, anos `3` | `32.05` | `Bronze` |
| compras `[1000, 2000, 500]`, anos `10` | `400.0` | `Ouro` |
| compras `[10000]`, anos `5` | `1025.0` | `Platina` |

Conta do terceiro caso negativo: soma `1000`, score de compras `100`, fidelidade `-15`, total `85.00`, faixa de `Prata`. O ano negativo não força `Crítico`; só o score final negativo o faz.

## Campos adicionais

Chaves além de `id`, `nome`, `compras` e `anos_ativo` são ignoradas. Não entram no score, não são copiadas para o retorno e não alteram a categoria. Exemplos: `email`, `cidade`, `telefone`, `observacao`.

Motivo: a especificação não define semântica para esses campos. Ecoá-los acoplaria o retorno a um esquema instável. Recusar o dicionário inteiro por causa de uma chave extra tornaria a função frágil diante de registros reais, que quase sempre trazem colunas a mais.

Campo obrigatório ausente não é preenchido com padrão. O acesso `dados["compras"]`, `dados["anos_ativo"]`, `dados["id"]` ou `dados["nome"]` levanta `KeyError`. Inventar `compras = []` ou `anos_ativo = 0` classificaria um registro incompleto como cliente real.

## Imutabilidade

A função não atribui chaves em `dados`, não faz `append`/`pop`/`sort`/`reverse`/`clear`/`extend` em `compras` e não reatribui elementos da lista. `sum` só lê. O dicionário devolvido é novo.

Não se faz cópia defensiva da lista de compras. Uma cópia dobraria a memória justamente no caso de histórico grande, e a especificação proíbe mutação, não exige cópia. Quem chamar a função pode manter a lista original intacta porque esta implementação não a escreve.

`id` e `nome` são os mesmos objetos string da entrada. Strings são imutáveis; “preservar” significa conservar o valor caractere a caractere.

## Volume e precisão

O histórico é percorrido uma única vez, em tempo linear e memória adicional constante (além do dicionário de quatro chaves). Não há ordenação, não há construção de uma segunda lista e não há chamada por item a um serviço externo. Listas longas (dezenas ou centenas de milhares de compras) são o caso esperado de uso, desde que caibam em memória.

A soma usa o `sum` de floats IEEE-754 do CPython. Erros binários de frações como `0.1` podem aparecer antes do `round`. A especificação manda arredondar a duas casas, e esse passo é o que estabiliza o score publicado. Não usamos `math.fsum`: a diferença só apareceria em somas enormes de frações não representáveis e, depois de `round(..., 2)`, quase sempre some. Preferimos o `sum` literal da fórmula. Se no futuro o dinheiro precisar ser exato ao centavo em históricos gigantes, a mudança seria somar em centavos inteiros; isso não está no núcleo atual e não foi implementado.

Não há teto artificial de score. Um histórico muito grande produz um score muito grande e cai em `Platina` a partir de 1000.

## Unicode

`id` e `nome` podem conter qualquer caractere Unicode (acentos, CJK, emoji, caracteres de controle que já venham na string). A função não aplica NFC/NFD, não remove marcas combinantes e não recodifica para ASCII. A comparação de identidade do texto é a da string Python já recebida.

A categoria `Crítico` também usa Unicode. As demais categorias são ASCII.

## O que esta função não faz

- Não valida CPF, e-mail ou formato do `id`.
- Não persiste, não ordena clientes e não compara um cliente com outro. Cada chamada é independente.
- Não distingue moeda. Os números de `compras` já estão na mesma unidade.
- Não aplica peso por recência: a primeira e a última compra contam igual. A especificação não tem data.
- Não lança exceção própria para score negativo ou categoria `Crítico`. Isso é resultado de negócio, não falha de cálculo.
