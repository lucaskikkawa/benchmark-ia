# Por que o esforço high foi pior que o medium? (Claude, Codex, Gemini)

Fonte: só as notas do avaliador (`avaliacao_avaliador.json`), N=30 por combinação (só run-1; sem consistência). Grok fora.

## Resposta curta

- A premissa **não vale para o haiku**: lá o **high foi MELHOR** (9,75 contra 9,66; +0,10).
- Nos outros 5 pares o high perdeu, e **em todos a causa dominante é timeout**. Em execuções sem timeout, o high empata ou fica levemente melhor em testes e rubrica.

## Método da decomposição

Para cada execução, perda = 10 − nota, separada em 4 partes que somam exatamente a perda:
- (a) **timeout**: se status = timeout, perda 10 (a nota vira 0);
- (b) **testes**: se não houve timeout, 0,7 × (100 − %testes)/10;
- (c) **rubrica**: se não houve timeout, 0,3 × (10 − rubrica);
- (d) **erro/cota**: se status = erro, perda total.

Média de cada parte nas 30 execuções. Contribuição para (high − medium) = perda_medium − perda_high, então as 4 contribuições somam a diferença de nota média. Positivo = favorece o high.

## Decomposição por par (pontos de nota média)

|Par|Medium|High|Δ total|(a) timeout|(b) testes|(c) rubrica|(d) erro/cota|
|-|-|-|-|-|-|-|-|
|haiku|9,66|9,75|**+0,10**|0,00|+0,04|+0,05|0,00|
|opus|9,70|9,39|**−0,31**|−0,33|0,00|+0,02|0,00|
|luna|9,09|9,00|**−0,09**|−0,33|+0,19|+0,05|0,00|
|sol|8,79|8,16|**−0,63**|−0,67|0,00|+0,03|0,00|
|argon|7,22|6,96|**−0,25**|−0,33|0,00|+0,08|0,00|
|flash|2,85|1,31|**−1,54**|−1,67|0,00|+0,13|0,00|

(d) é zero porque não sobrou nenhum status de erro. As 7 execuções do opus-high que falharam por cota foram refeitas antes (backup em `_erros_cota/`); as refeitas entram normalmente.

### (a) Timeouts em cada lado

- **haiku**: 0 no medium, 0 no high.
- **opus**: 0 no medium. 1 no high: 05-cli-gemini, limite 180 s, entrega com 100% dos testes.
- **luna**: 0 no medium. 1 no high: 07-performance-grok, 180 s, 0% dos testes.
- **sol**:
  - medium, 2: 09-api-gemini e 09-api-grok;
  - high, 4: 05-cli-claude (100%), 05-cli-gemini (27%), 08-testes-claude (6%), 08-testes-gemini (100%).
- **argon**:
  - medium, 7: 01-funcao-claude, 05-cli-grok, 06-multiarquivo-claude, 06-multiarquivo-codex, 08-testes-claude, 08-testes-codex, 10-ambigua-claude. Destes, 4 com 100% dos testes;
  - high, 8, todos com limite de 180 s: 01-funcao-claude, 03-refatoracao-claude, 04-dados-claude, 04-dados-codex, 08-testes-claude, 08-testes-codex, 08-testes-grok, 10-ambigua-claude. Destes, 5 com 100% dos testes.
- **flash**: 21 no medium (8 com 100% dos testes) e 26 no high (4 com 100%). No high, só 4 de 30 terminaram.

### (b) e (c) Execuções sem timeout

- **(b) Testes**: as execuções sem timeout do high passam em 100% dos testes em todos os pares. Únicas falhas parciais:
  - haiku: 2 no medium (99,4%), 0 no high;
  - luna: 4 de cada lado, mas o high passa mais testes (99,3% contra 96,5%).
- **(c) Rubrica**: é igual ou maior no high em todos os pares (ex.: flash 9,50 contra 8,33; argon 8,32 contra 8,04).

## Tempo de agente (todas as 30, em s)

|Par|Medium: média / mediana|High: média / mediana|Perto do limite (≥80%, sem timeout) M / H|
|-|-|-|-|
|haiku|28 / 21|50 / 42|0 / 0|
|opus|43 / 32|51 / 43|0 / 0|
|luna|20 / 20|33 / 24|0 / 0|
|sol|63 / 47|87 / 68|0 / 1|
|argon|121 / 94|134 / 128|1 / 2|
|flash|195 / 180|209 / 180|2 / 2|

O high é mais lento em todos os pares: de +8 s (opus) a +34 s (argon, pela mediana). Média e mediana incluem os timeouts, que contam pelo próprio limite.

## O limite de 3 min pesou mais no high?

- 31 das 40 tarefas usam `timeout_min: 3` (180 s); 9 usam 300 s. O PLANO fala em 5 min padrão, mas permite o meta.yaml reduzir.
- Timeouts nos 6 pares somados: medium 30 (21 com limite de 180 s e 9 com 300 s); high 40 (30 com 180 s e 10 com 300 s). **Os 10 timeouts a mais do high caíram nas tarefas de 180 s.**
- **Não dá para dizer com certeza quantos passariam com 5 min**: essas execuções não foram refeitas com 300 s (os backups `_timeouts_*` são só do Grok).
- Como aproximação, conto os timeouts cuja entrega parcial já passa em 100% dos testes ocultos:
  - medium: 12 (argon 4, flash 8);
  - high: 12 (opus 1, sol 2, argon 5, flash 4).
- Contrafactual 1: esses timeouts contam como concluídos, com a rubrica média do modelo. O Δ high − medium fica assim:
  - haiku +0,10; opus +0,01; luna −0,09;
  - sol −0,00; argon +0,07; flash −2,76.
- Contrafactual 2: só os timeouts com 100% em tarefas de 180 s viram concluídos.
  - sol: o Δ ainda melhora (−0,32 contra −0,63).
  - argon: o high passa à frente (+0,70).

## Opinião

**EVIDÊNCIA**
- Em 5 dos 6 pares, a perda do high é 100% ou mais explicada por timeout. Por exemplo, sol −0,67 de −0,63 e flash −1,67 de −1,54. Testes e rubrica sem timeout ajudam o high (+0,02 a +0,24).
- O high é sistematicamente mais lento (+8 a +34 s de mediana). Os timeouts a mais do high estão todos nas tarefas de 180 s: 30 contra 21.
- Muitos timeouts não são soluções ruins: 12 de cada lado já tinham entrega que passa em 100% dos testes. Para opus, sol e argon, essas entregas sozinhas explicam quase toda a diferença: o Δ vai a +0,01, −0,00 e +0,07 no contrafactual 1.
- haiku: o high foi melhor (+0,10), sem timeouts.
- flash: colapsa nos dois esforços (21 e 26 timeouts de 30). Mesmo dando crédito às entregas completas, o high continua bem pior (−2,76), então ali não é só o limite.
- luna: a diferença é pequena (−0,09), só 1 timeout no high, sem entrega.

**PALPITE**
- O high não é pior em qualidade: ele pensa mais e estoura o relógio. Com o limite de 5 min do PLANO, opus, sol e argon high provavelmente empatariam ou superariam o medium.
- Para cravar, seria preciso refazer com 300 s os timeouts do high e do medium desses pares (cerca de 70 execuções).
- No flash high, o palpite é outro problema: loop, excesso de ferramentas ou cota/latência da API.
