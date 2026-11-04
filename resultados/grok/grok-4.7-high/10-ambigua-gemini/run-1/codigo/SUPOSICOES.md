# Suposições de design — `classificar_cliente`

Este documento fecha o que a especificação deixou em aberto. O núcleo inequívoco não é reinterpretado: o score continua sendo `round(soma(compras) * 0.1 + anos_ativo * 5, 2)`. As decisões abaixo só cobrem categoria, leitura de casos ambíguos e o contrato de entrada e saída em torno dessa fórmula.

## 1. Escopo do que foi decidido

A especificação já define os quatro campos de entrada (`id`, `nome`, `compras`, `anos_ativo`), a fórmula do score, o arredondamento, as quatro chaves de saída e a imutabilidade da entrada.

Ficou em aberto, e é decidido aqui:

- nomes das categorias e as faixas de score que as separam;
- compras com valor negativo (estorno/devolução ou descarte);
- `anos_ativo` negativo;
- campos adicionais na entrada;
- também, por consequência: lista vazia, duplicatas, ausência de data, Unicode, tipos fora do contrato, NaN e volume grande.

A função é pura: sem I/O, sem relógio, sem estado global, sem aleatoriedade. O mesmo dicionário produz sempre o mesmo resultado.

## 2. Fórmula, sem ajuste silencioso

```text
soma_compras = sum(compras)          # um único passe, ordem irrelevante
score_base   = soma_compras * 0.1    # 1 ponto a cada 10 unidades monetárias líquidas
score_fidel  = anos_ativo * 5        # 1 ano equivale a 50 unidades líquidas (50 * 0.1 = 5)
score        = round(score_base + score_fidel, 2)
```

Premissa de unidade: os valores de `compras` estão na mesma unidade monetária (por exemplo, reais). A função não converte moeda nem aplica inflação, porque a entrada não traz moeda nem data.

Equivalência usada para desenhar as faixas: `valor_liquido_equivalente = score * 10`. Um ano de relacionamento pesa o mesmo que 50 unidades de compra líquida. Tempo sozinho não alcança os níveis altos: 10 anos sem compra valem 50 pontos (limite do bronze); ouro (400) exigiria 80 anos. Níveis altos dependem de compra líquida.

Não há teto nem piso no score. Dois clientes da mesma categoria continuam ordenáveis pelo score. A categoria é uma partição grossa para ação de CRM; o score é a chave fina de ranking. Isso importa em histórico longo: um cliente com dezenas de milhares de compras não satura num “máximo” que apagaria a diferença entre ele e outro diamante.

O score oficial é o valor **depois** do `round`. A categoria lê esse número, não o valor intermediário. Assim, um resultado que a aritmética deixaria em 49,996 e o `round` levaria a 50,00 entra na faixa de 50.

`-0.0` é normalizado para `0.0`. São o mesmo número (`-0.0 == 0.0`), mas o sinal espúrio de zero negativo confunde leitura e serialização. A categoria não muda: zero é iniciante.

## 3. Compras negativas entram na soma (são estornos)

Decisão: todo item numérico de `compras` entra em `sum`, inclusive negativos e zero.

Leitura de negócio: valor negativo é estorno, devolução ou abatimento já lançado no histórico. O score de compras mede contribuição líquida, não volume bruto. Ignorar negativos premiaria quem compra e devolve muito.

Consequências:

- compra 1000 e estorno 200 produzem soma 800 e score base 80, não 100;
- histórico só de estornos produz score base negativo e pode cair em `em_risco`;
- zero não altera a soma (compra anulada ou lançamento neutro) e é mantido, não filtrado.

Alternativas rejeitadas:

- descartar negativos ou trocá-los por zero: diverge de “10% da soma dos valores” e infla o score;
- limitar o desconto do estorno ao valor da compra original: a lista não tem vínculo entre lançamentos, só valores. Não há como saber qual estorno corresponde a qual compra sem inventar um emparelhamento.

## 4. Anos ativos negativos aplicam a fórmula

Decisão: `anos_ativo` entra na multiplicação por 5 mesmo quando é negativo. Não há `max(anos_ativo, 0)` nem valor absoluto.

Motivo: a regra inequívoca é `anos_ativo * 5`. Corrigir em silêncio mudaria o score que a especificação manda calcular. Tempo negativo é tratado como anomalia de dado que reduz o score, não como dado a ser reescrito.

Se o chamador passar um não inteiro (a especificação pede `int`, mas o valor pode chegar fracionário), a função também não trunca. Só o score final é arredondado a 2 casas. Truncar o ano antes da multiplicação seria outra correção silenciosa.

Tempo negativo não cria uma categoria própria. Ele apenas empurra o score para baixo; a faixa resultante segue a tabela da seção 8. Exemplo: compras líquidas de 200 (base 20) e `anos_ativo = -3` (fidelidade −15) dão score 5,00, categoria `iniciante`.

## 5. Campos adicionais e contrato de saída

Decisão: chaves além de `id`, `nome`, `compras` e `anos_ativo` são ignoradas. Não são lidas, copiadas, validadas nem alteradas.

A saída tem exatamente estas chaves, nesta ordem:

| chave | regra |
| --- | --- |
| `id` | o mesmo valor recebido, sem normalizar |
| `nome` | o mesmo valor recebido, sem normalizar |
| `score` | número do `round` (float; `0.0` no lugar de `-0.0`) |
| `categoria` | um dos tokens da seção 8 |

Motivo de um contrato fechado: o chamador pode anexar metadados (`email`, `loja`, `cpf`) sem vê-los vazar na resposta nem quebrar consumidores que esperam um formato estável. A classificação não depende desses campos porque a especificação não lhes dá peso.

Campos obrigatórios ausentes propagam `KeyError`. Itens não numéricos em `compras`, ou `anos_ativo` não numérico, propagam `TypeError` a partir de `sum` ou da multiplicação. Não há mensagem traduzida nem valor default: default esconderia entrada inválida e mudaria o score (por exemplo, tratar ausência de `anos_ativo` como 0).

`bool` é subtipo de `int` em Python. `True` somaria 1 e `False` somaria 0. Isso está fora do contrato (a lista é de `float | int` de compras). A função não filtra bool, porque filtrar mudaria a soma literal.

## 6. Lista vazia, ordem, duplicatas e recência

- Lista vazia: `sum([]) == 0`. O score é só `anos_ativo * 5`. Cliente sem compras e com 0 anos tem score `0.0` e categoria `iniciante` (ainda não há relação negativa; também não há mérito).
- A ordem dos lançamentos não importa. A soma é comutativa. A função não ordena a lista.
- Valores repetidos contam todas as vezes. A lista é histórico de valores, não um conjunto de produtos.
- Não há decaimento por recência nem peso maior para a última compra. A entrada não traz datas. Inventar “a última compra vale mais” exigiria tratar a posição na lista como tempo, o que a especificação não diz.
- Não há corte de outlier. Uma compra muito alta pode levar a `diamante`. Winsorizar violaria a soma.

## 7. Arredondamento e precisão

Usa-se o `round` nativo de Python 3, como escrito na especificação: meia unidade arredonda para o par mais próximo (half to even), sobre float binário IEEE-754.

Não se usa `decimal.Decimal` nem `math.fsum`. Os dois podem divergir do `sum` + `round` exigidos no núcleo, em empates de meio e em somas longas. A reprodutibilidade com a fórmula literal pesa mais do que ganho de precisão.

Limite conhecido, aceito de propósito: acima de 2^53, inteiros não cabem exatamente em float. Históricos longos de valores moderados são o caso alvo (“grande volume”); cada chamada faz um único `sum` em memória extra O(1), sem copiar `compras`.

`NaN` não satisfaz nenhuma comparação `score >= limiar` e cai em `em_risco`. Não é promovido a diamante. `+inf` cai em `diamante` (faixa aberta no topo). `-inf` cai em `em_risco`. NaN e infinito estão fora do contrato; o comportamento acima é só a consequência estável das comparações, para não conceder nível alto a um score inválido.

## 8. Categorias

A categoria é função apenas do score final. Um eixo só, não uma matriz “gasto × tempo”.

Motivo: a saída pede uma string. Uma matriz precisaria de uma regra extra quando os sinais discordam (muito gasto e pouco tempo, ou o contrário). O score já combina os dois com pesos definidos. Bandear o score mantém a categoria auditável: quem conhece o score sabe a faixa, sem olhar a composição.

Tokens estáveis, em minúsculas, sem acento e sem espaço, para filtro, log e comparação exata:

| categoria | condição sobre o score | equivalente se o score viesse só de compras | leitura |
| --- | --- | --- | --- |
| `em_risco` | `score < 0` | valor líquido negativo, já descontado o bônus de tempo | não conceder benefício; revisar estornos ou o dado de tempo |
| `iniciante` | `0 <= score < 50` | até 500 | ativação; inclui o zero |
| `bronze` | `50 <= score < 150` | de 500 até abaixo de 1.500 | relação inicial consistente, ou cerca de 10 anos sem compra |
| `prata` | `150 <= score < 400` | de 1.500 até abaixo de 4.000 | base fiel |
| `ouro` | `400 <= score < 1000` | de 4.000 até abaixo de 10.000 | alto valor |
| `platina` | `1000 <= score < 2500` | de 10.000 até abaixo de 25.000 | muito alto valor |
| `diamante` | `score >= 2500` | 25.000 ou mais | topo, faixa aberta |

O limite inferior de cada faixa é inclusivo e o superior é exclusivo. Quem acerta o corte sobe. Exemplo: 150,00 é `prata`, 149,99 é `bronze`. 50,00 é `bronze`. 0,00 é `iniciante`, não `em_risco`: cliente novo não é tratado como conta em prejuízo.

A progressão depois de bronze é aproximadamente geométrica, com fator perto de 2,5 (150, 400, 1000, 2500). Há resolução bastante para ações diferentes (ativar, reter, recompensar, atender um a um) sem uma faixa nova a cada degrau pequeno de score. O primeiro salto, de 0 a 50, é mais curto de propósito: separa quem ainda não tem sinal relevante de quem já tem ou ~500 de compra líquida ou ~10 anos de cadastro.

`em_risco` não é uma medalha. É um segmento de status abaixo do primeiro nível. As medalhas (`bronze` até `diamante`) só existem para score não negativo.

Nenhuma dessas ações sugeridas é retornada. São a justificativa das faixas. A saída leva só o token.

### Exemplos conferidos com a implementação

| compras | anos | soma | score | categoria |
| --- | ---: | ---: | ---: | --- |
| `[]` | 0 | 0 | 0.0 | `iniciante` |
| `[10, 20, 30]` | 1 | 60 | 11.0 | `iniciante` |
| `[490]` | 0 | 490 | 49.0 | `iniciante` |
| `[500]` | 0 | 500 | 50.0 | `bronze` |
| `[1000, -200]` | 3 | 800 | 95.0 | `bronze` |
| `[999]` | 10 | 999 | 149.9 | `bronze` |
| `[1000]` | 10 | 1000 | 150.0 | `prata` |
| `[200]` | -3 | 200 | 5.0 | `iniciante` |
| `[-1000]` | 1 | -1000 | -95.0 | `em_risco` |
| `[100, -40, -70]` | 2 | -10 | 9.0 | `iniciante` |
| `[4000]` | 0 | 4000 | 400.0 | `ouro` |
| `[10000]` | 0 | 10000 | 1000.0 | `platina` |
| `[24990]` | 0 | 24990 | 2499.0 | `platina` |
| `[25000]` | 0 | 25000 | 2500.0 | `diamante` |
| `[300000]` | 10 | 300000 | 30050.0 | `diamante` |

Conta dos casos menos óbvios:

- `[1000, -200]` e 3 anos: base `800 * 0.1 = 80`, fidelidade `15`, score `95.00`, bronze.
- `[999]` e 10 anos: base `99.9`, fidelidade `50`, score `149.90`, ainda bronze; 0,10 a mais de compra líquida (ou qualquer combinação que some 0,10 no score) cruzaria para prata.
- `[-1000]` e 1 ano: base `-100`, fidelidade `5`, score `-95.00`, em risco.
- `[300000]` e 10 anos: base `30000`, fidelidade `50`, score `30050.00`, diamante, sem truncar no limiar 2500.

## 9. Imutabilidade e volume

A função não atribui chaves em `dados`, não faz append, sort, reverse, clear nem estende `compras`, e não guarda referência mutável da lista na saída. `sum` só lê. `id` e `nome` são repassados como vieram (strings são imutáveis; a mesma referência é preservada).

Custo por chamada: O(n) no tamanho de `compras`, memória extra O(1) além do dicionário de quatro chaves. Não há cópia defensiva da lista: copiar um histórico grande gastaria memória sem necessidade, já que a função não escreve na lista. Um iterador de uso único seria consumido; o contrato da especificação é uma lista, que permanece reutilizável.

## 10. Unicode e identidade de texto

`id` e `nome` são copiados logicamente sem `strip`, `casefold`, NFC/NFKC ou remoção de acentos. “José” e “Jose” permanecem diferentes. Formas compostas e decompostas (NFC e NFD) também permanecem diferentes: a função não é um cadastro que deduplica pessoas. Espaços nas pontas são significativos pelo mesmo motivo.

Caracteres não latinos, emoji e sinais de combinação passam intactos. Nada na classificação depende do conteúdo textual; o score não usa o nome.

## 11. Alternativas rejeitadas (resumo)

| alternativa | por que não |
| --- | --- |
| Ignorar ou zerar compras negativas | deixa de ser a soma dos valores e premia devolução |
| Zerar ano negativo | deixa de ser `anos_ativo * 5` |
| Matriz gasto × tempo com desempate ad hoc | a saída é uma categoria; o score já é o combinador oficial |
| Teto de score no diamante | apaga ranking entre clientes de cauda longa |
| Peso por recência ou por posição na lista | não há data; a posição não foi definida como tempo |
| `Decimal` ou `math.fsum` | pode divergir do `sum` + `round` do núcleo |
| Copiar campos extras para a saída | abre o contrato e vaza metadado |
| Preencher campo faltante com zero | mascara erro e altera o score |
| Normalizar Unicode do nome | cola identidades que o sistema de origem mantém distintas |

## 12. Resumo operacional

1. Somar todas as compras, com sinal.
2. Somar 5 pontos por ano ativo, com sinal.
3. Arredondar a soma a 2 casas com `round` e trocar `-0.0` por `0.0`.
4. Mapear o score à faixa inclusiva inferior da seção 8.
5. Devolver só `id`, `nome`, `score` e `categoria`, sem modificar a entrada.
