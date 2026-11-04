# Suposições — classificação de clientes e score de fidelidade

Este documento fecha os pontos que a especificação deixou em aberto e registra as premissas usadas em `classificar_cliente` (`solucao.py`). O cálculo do score em si não é uma suposição: ele segue o núcleo fechado.

## Score (núcleo aplicado sem ajuste)

```text
score = round(soma(compras) * 0.1 + anos_ativo * 5, 2)
```

- A soma é a soma algébrica de todos os itens, numa única passagem, em `float`.
- `round` é o builtin do Python (arredondamento bancário, metade para o par mais próximo) aplicado ao valor já combinado, com duas casas.
- A categoria é decidida **depois** do arredondamento, sobre o mesmo número colocado em `"score"`. Assim o segmento nunca contradiz o valor devolvido. Exemplo: soma `999.96` e `anos_ativo` `0` produz bruto `99.996`, que arredonda para `100.0` e cai em `prata`, não em `bronze`.
- Não há teto, piso nem normalização. Score negativo é um resultado válido.
- Não se devolvem parcelas separadas (base de compras e fidelidade). O contrato estável tem só as quatro chaves obrigatórias; parcelas extras quebrariam comparação estrita do dicionário e vazariam detalhe que o chamador pode recomputar.

### Precisão

Listas grandes continuam em uma passagem e memória extra constante (além do dicionário de saída). Não se copia `compras`. A soma usa `float` de IEEE 754 porque a especificação pede `round(..., 2)` sobre essa conta, não aritmética decimal. Somas muito grandes de centavos podem sofrer erro binário antes do arredondamento (por exemplo valores que não têm representação exata, como muitos múltiplos de `0.1`). Não se usa `Decimal`: trocar o tipo mudaria casos de meio exato em relação ao `round` nativo que a especificação cita.

`int` e `float` podem aparecer misturados na mesma lista. `bool` não entra, embora seja subclasse de `int`.

## Categorias e faixas

A categoria depende só do score final arredondado. Dois clientes com o mesmo score recebem o mesmo segmento, seja o score vindo de compra ou de tempo de casa. Uma matriz gasto × anos foi descartada: dobra a tabela de regras, cria empates de leitura (“muito gasto e pouco tempo” versus “pouco gasto e muito tempo”) e não cabe num único rótulo sem um segundo eixo no retorno.

Os nomes são identificadores estáveis, em minúsculas, sem acento e sem espaço, para comparação e JSON. Não são rótulos de tela. Um mapa de UI pode exibir “Prata” ou “Crítico” sem mudar o contrato.

O score vale cerca de R$ 10 de compra líquida por ponto, mais 5 pontos por ano. As faixas fazem o gasto dominar e impedem que só o tempo de casa promova o cliente a um tier alto: 20 anos sem compra valem 100 pontos e param em `prata`.

| Categoria   | Score arredondado | Leitura operacional |
|-------------|-------------------|---------------------|
| `critico`   | `< 0`             | Valor líquido negativo: estornos (e, se houver, anos negativos) superam compras e fidelidade. |
| `bronze`    | `[0, 100)`        | Entrada ou baixo volume. Inclui score `0` (sem compras e sem anos). |
| `prata`     | `[100, 350)`      | Por volta de R$ 1.000 líquidos, ou a combinação equivalente com anos. |
| `ouro`      | `[350, 1000)`     | Por volta de R$ 3.500 líquidos, ou combinação equivalente. |
| `platina`   | `[1000, 3000)`    | Por volta de R$ 10.000 líquidos. |
| `diamante`  | `>= 3000`         | Por volta de R$ 30.000 líquidos ou mais. |

Limite inferior inclusivo. `100.0` é `prata`; `99.99` é `bronze`; `350.0` é `ouro`; `1000.0` é `platina`; `3000.0` é `diamante`.

`bronze` em score zero trata cliente novo como segmento válido, não como erro. `critico` fica reservado a score negativo, para um processo de auditoria separar relação sem movimento de relação com saldo negativo.

## Compras negativas

Entram na soma. São estornos, devoluções ou ajustes, não ruído a descartar.

Motivo: a regra fechada fala em 10% da **soma dos valores**. Zerar ou ignorar negativos inflaria o score e esconderia devolução. Não há, na entrada, um tipo de lançamento que permita separar estorno de desconto; o sinal é a única informação.

Exemplos:

- `[100.0, -40.0]` e `2` anos → soma `60`, base `6`, fidelidade `10`, score `16.0`, categoria `bronze`.
- `[50, -80]` e `1` ano → soma `-30`, base `-3`, fidelidade `5`, score `2.0`, categoria `bronze` (o ano ainda segura o saldo acima de zero).
- `[-200]` e `0` anos → score `-20.0`, categoria `critico`.

Lista vazia soma `0`. O score fica só com a fidelidade (`anos_ativo * 5`).

## Anos ativos negativos

A fórmula fechada é aplicada literalmente: `anos_ativo * 5` pode reduzir o score. Não se faz clamp para zero e não se rejeita a linha.

Alternativas rejeitadas:

- **Clamp em zero.** Esconderia dado inválido dentro de um score “normal” e impediria auditoria.
- **Exceção.** Um único registro ruim derrubaria um lote grande. A função deve percorrer volume alto de compras; o mesmo critério vale para não abortar o cliente por um ano inconsistente.
- **Categoria própria para ano negativo.** A especificação pede um segmento por score. Dois eixos (score e qualidade do dado) exigiriam outra chave. Ano negativo com compra alta permanece no tier do score positivo; o chamador reconcilia `anos_ativo` na origem. Ano negativo que leve o score abaixo de zero aparece como `critico`.

Exemplo: compras `[100]` e `anos_ativo` `-3` → base `10`, fidelidade `-15`, score `-5.0`, categoria `critico`.

`anos_ativo` não inteiro, se for `float` real (por exemplo `2.5`), entra na mesma fórmula (`12.5` pontos de fidelidade). A especificação declara `int`; aceitar `float` evita falha artificial quando a série já veio como número real. Não se trunca.

## Campos adicionais e formato da entrada

- A entrada precisa das chaves `id`, `nome`, `compras` e `anos_ativo`. Chave ausente propaga `KeyError`.
- Qualquer outro campo (`email`, `cidade`, `tags`, metadados) é ignorado e **não** é copiado para a saída. Isso mantém o schema estável e evita ecoar dado que o chamador não pediu neste contrato.
- `id` e `nome` são devolvidos por identidade, sem `strip`, sem normalização Unicode (NFC/NFD), sem casefold e sem recodificação. `"José"`, `"李明"`, `"Åsa"`, ids com acento ou emoji e nomes com espaço nas pontas permanecem byte a byte iguais. Dois nomes que só diferem por acento continuam distintos.
- A saída tem exatamente as chaves `id`, `nome`, `score`, `categoria`, nesta ordem de inserção.
- `compras` precisa ser `list` ou `tuple`. `str` e `bytes` são rejeitados de propósito: são iteráveis de caracteres, e somá-los seria um erro silencioso. A lista não é ordenada, filtrada nem reescrita.
- Cada item de `compras` precisa ser `int` ou `float`, e não `bool`. String numérica (`"10.0"`), `None`, `NaN` não é checado à parte: `NaN` falha a soma útil porque `NaN` é `float` e contaminaria o score; tratamos `NaN` e infinitos como erro (`ValueError`) para um lote não publicar score `nan`. Ver implementação: após aceitar o tipo numérico, `NaN` e `±inf` são recusados.
- `dados` que não seja `dict` levanta `TypeError`.

## Imutabilidade e pureza

- A função não atribui em `dados`, não faz `pop`/`update`/`clear` e não chama métodos que alterem `compras` (sem `sort`, `append`, `reverse` ou fatia atribuída).
- O retorno é um dicionário novo.
- Não há estado global nem cache. Chamadas repetidas com o mesmo conteúdo produzem o mesmo resultado e deixam a entrada intacta, inclusive a identidade dos objetos `id` e `nome` quando são strings.

## O que fica de fora de propósito

- Não se infere moeda, inflação nem ticket médio. Os valores já chegam na mesma unidade.
- Não se pondera recência: a lista é um histórico sem data. Sem timestamp, qualquer decaimento seria inventado.
- Não se separa quantidade de pedidos versus valor. Um pedido de 1000 e dez de 100 com a mesma soma geram o mesmo score.
- Não se traduz a categoria para o idioma do nome do cliente. O segmento é código, não texto localizado.
