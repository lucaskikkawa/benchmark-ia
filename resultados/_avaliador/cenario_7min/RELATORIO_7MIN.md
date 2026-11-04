# Cenário “limite de 7 min” (420 s) — Claude, Codex e Gemini

As 70 run-1 que deram timeout no oficial foram refeitas com 420 s. Neste cenário elas substituem as originais; o resto é igual ao oficial (`notas_avaliador.csv`), N=30 por combinação, sem Grok, sem consistência. Juízes: 2 neutros (≠ empresa resolvedora, ≠ autora da tarefa), código anonimizado, sem penalidade de atraso. **Versão i**: timeout = 0 (regra padrão). **Versão ii**: os timeouts de novo são julgados pelo que está em `codigo/` (%testes + rubrica).

Arquivos: `notas_7min.csv` (360 execuções), `notas_7min_refeitas.json` (70), `matriz_7min.csv`, `auditoria_7min.json`; nas pastas run-N, `avaliacao_avaliador_7min.json`. Oficiais intocados.

## (a) Ranking das 12 combinações

|Combinação|Oficial (#)|7 min i (#)|7 min ii (#)|Refeitas|Timeout de novo|
|-|-|-|-|-|-|
|claude-haiku-5-5-high|9,75 (1)|9,75 (1)|9,75 (1)|0|0|
|claude-opus-5-5-high|9,39 (4)|9,71 (2)|9,71 (2)|1|0|
|claude-opus-5-5-medium|9,70 (2)|9,70 (3)|9,70 (3)|0|0|
|claude-haiku-5-5-medium|9,66 (3)|9,66 (4)|9,66 (4)|0|0|
|gpt-6.1-sol-medium|8,79 (7)|9,41 (5)|9,41 (5)|2|0|
|gpt-6.1-sol-high|8,16 (8)|9,39 (6)|9,39 (6)|4|0|
|gpt-6-luna-high|9,00 (6)|9,29 (7)|9,29 (7)|1|0|
|gpt-6-luna-medium|9,09 (5)|9,09 (8)|9,09 (9)|0|0|
|gemini-4-argon-medium|7,22 (9)|9,09 (9)|9,09 (10)|7|1|
|gemini-4-argon-high|6,96 (10)|8,52 (10)|9,18 (8)|8|3|
|gemini-3.8-flash-medium|2,85 (11)|7,85 (11)|8,80 (11)|21|5|
|gemini-3.8-flash-high|1,31 (12)|5,05 (12)|7,09 (12)|26|14|

## (b) Médias por empresa (média das 4 combinações)

|Empresa|Oficial|7 min i|7 min ii|
|-|-|-|-|
|claude|9,62|9,71|9,71|
|codex|8,76|9,30|9,30|
|gemini|4,59|7,63|8,54|

## (c) high − medium por par

|Par|Oficial|7 min i|7 min ii|
|-|-|-|-|
|haiku|+0,10|+0,10|+0,10|
|opus|-0,31|+0,01|+0,01|
|luna|-0,09|+0,19|+0,19|
|sol|-0,63|-0,02|-0,02|
|argon|-0,25|-0,57|+0,08|
|flash|-1,54|-2,80|-1,71|

## Execuções refeitas

|Combinação|Tarefa|Status 7 min|Duração (s)|%testes|Rubrica|Nota oficial|Nota i|Nota ii|
|-|-|-|-|-|-|-|-|-|
|claude-opus-5-5-high|05-cli-gemini|ok|29|100|9,00|0,00|9,70|9,70|
|gemini-3.8-flash-high|01-funcao-claude|timeout|420|0|0,00|0,00|0,00|0,00|
|gemini-3.8-flash-high|01-funcao-grok|ok|360|100|7,00|0,00|9,10|9,10|
|gemini-3.8-flash-high|02-bug-claude|ok|349|100|7,50|0,00|9,25|9,25|
|gemini-3.8-flash-high|02-bug-grok|ok|378|100|7,00|0,00|9,10|9,10|
|gemini-3.8-flash-high|03-refatoracao-claude|timeout|420|100|9,00|0,00|0,00|9,70|
|gemini-3.8-flash-high|03-refatoracao-codex|timeout|420|47|3,00|0,00|0,00|4,22|
|gemini-3.8-flash-high|03-refatoracao-grok|ok|282|100|7,50|0,00|9,25|9,25|
|gemini-3.8-flash-high|04-dados-claude|timeout|420|0|0,00|0,00|0,00|0,00|
|gemini-3.8-flash-high|04-dados-codex|timeout|420|100|8,00|0,00|0,00|9,40|
|gemini-3.8-flash-high|04-dados-grok|timeout|420|0|0,00|0,00|0,00|0,00|
|gemini-3.8-flash-high|05-cli-claude|timeout|420|100|6,50|0,00|0,00|8,95|
|gemini-3.8-flash-high|05-cli-codex|timeout|420|0|0,00|0,00|0,00|0,00|
|gemini-3.8-flash-high|05-cli-grok|timeout|420|7|0,00|0,00|0,00|0,47|
|gemini-3.8-flash-high|06-multiarquivo-claude|ok|352|100|6,50|0,00|8,95|8,95|
|gemini-3.8-flash-high|06-multiarquivo-codex|ok|307|100|9,00|0,00|9,70|9,70|
|gemini-3.8-flash-high|06-multiarquivo-grok|ok|365|100|8,50|0,00|9,55|9,55|
|gemini-3.8-flash-high|07-performance-claude|ok|358|100|6,50|0,00|8,95|8,95|
|gemini-3.8-flash-high|07-performance-codex|ok|245|100|7,00|0,00|9,10|9,10|
|gemini-3.8-flash-high|07-performance-grok|ok|358|100|7,00|0,00|9,10|9,10|
|gemini-3.8-flash-high|08-testes-claude|timeout|420|6|0,00|0,00|0,00|0,41|
|gemini-3.8-flash-high|08-testes-codex|ok|395|100|10,00|0,00|10,00|10,00|
|gemini-3.8-flash-high|08-testes-grok|timeout|420|100|10,00|0,00|0,00|10,00|
|gemini-3.8-flash-high|09-api-claude|timeout|420|100|6,50|0,00|0,00|8,95|
|gemini-3.8-flash-high|09-api-codex|ok|369|100|10,00|0,00|10,00|10,00|
|gemini-3.8-flash-high|09-api-grok|timeout|420|100|7,00|0,00|0,00|9,10|
|gemini-3.8-flash-high|10-ambigua-claude|timeout|420|0|0,00|0,00|0,00|0,00|
|gemini-3.8-flash-medium|01-funcao-claude|ok|232|100|8,00|0,00|9,40|9,40|
|gemini-3.8-flash-medium|01-funcao-grok|ok|269|100|7,50|0,00|9,25|9,25|
|gemini-3.8-flash-medium|02-bug-claude|ok|267|100|6,50|0,00|8,95|8,95|
|gemini-3.8-flash-medium|02-bug-grok|ok|211|100|8,00|0,00|9,40|9,40|
|gemini-3.8-flash-medium|03-refatoracao-claude|ok|311|100|9,00|0,00|9,70|9,70|
|gemini-3.8-flash-medium|03-refatoracao-codex|ok|277|100|9,00|0,00|9,70|9,70|
|gemini-3.8-flash-medium|03-refatoracao-grok|ok|183|100|8,50|0,00|9,55|9,55|
|gemini-3.8-flash-medium|04-dados-claude|ok|369|100|6,00|0,00|8,80|8,80|
|gemini-3.8-flash-medium|04-dados-codex|ok|345|100|7,50|0,00|9,25|9,25|
|gemini-3.8-flash-medium|04-dados-grok|ok|331|100|8,00|0,00|9,40|9,40|
|gemini-3.8-flash-medium|05-cli-codex|ok|326|100|9,00|0,00|9,70|9,70|
|gemini-3.8-flash-medium|05-cli-grok|timeout|420|100|8,00|0,00|0,00|9,40|
|gemini-3.8-flash-medium|06-multiarquivo-grok|ok|236|100|8,50|0,00|9,55|9,55|
|gemini-3.8-flash-medium|07-performance-claude|ok|166|100|7,50|0,00|9,25|9,25|
|gemini-3.8-flash-medium|07-performance-grok|ok|220|100|7,00|0,00|9,10|9,10|
|gemini-3.8-flash-medium|08-testes-claude|timeout|420|6|0,00|0,00|0,00|0,41|
|gemini-3.8-flash-medium|08-testes-codex|timeout|420|100|9,50|0,00|0,00|9,85|
|gemini-3.8-flash-medium|08-testes-grok|ok|366|100|9,50|0,00|9,85|9,85|
|gemini-3.8-flash-medium|09-api-claude|timeout|420|100|6,50|0,00|0,00|8,95|
|gemini-3.8-flash-medium|09-api-grok|ok|415|100|7,00|0,00|9,10|9,10|
|gemini-3.8-flash-medium|10-ambigua-claude|timeout|420|0|0,00|0,00|0,00|0,00|
|gemini-4-argon-high|01-funcao-claude|ok|201|100|6,50|0,00|8,95|8,95|
|gemini-4-argon-high|03-refatoracao-claude|timeout|420|100|9,00|0,00|0,00|9,70|
|gemini-4-argon-high|04-dados-claude|ok|180|100|5,50|0,00|8,65|8,65|
|gemini-4-argon-high|04-dados-codex|ok|347|100|7,00|0,00|9,10|9,10|
|gemini-4-argon-high|08-testes-claude|timeout|420|100|10,00|0,00|0,00|10,00|
|gemini-4-argon-high|08-testes-codex|ok|298|100|10,00|0,00|10,00|10,00|
|gemini-4-argon-high|08-testes-grok|ok|265|100|10,00|0,00|10,00|10,00|
|gemini-4-argon-high|10-ambigua-claude|timeout|420|0|0,00|0,00|0,00|0,00|
|gemini-4-argon-medium|01-funcao-claude|ok|125|100|5,00|0,00|8,50|8,50|
|gemini-4-argon-medium|05-cli-grok|ok|141|100|6,50|0,00|8,95|8,95|
|gemini-4-argon-medium|06-multiarquivo-claude|ok|75|100|7,50|0,00|9,25|9,25|
|gemini-4-argon-medium|06-multiarquivo-codex|ok|63|100|9,00|0,00|9,70|9,70|
|gemini-4-argon-medium|08-testes-claude|ok|171|100|9,50|0,00|9,85|9,85|
|gemini-4-argon-medium|08-testes-codex|ok|184|100|10,00|0,00|10,00|10,00|
|gemini-4-argon-medium|10-ambigua-claude|timeout|420|0|0,00|0,00|0,00|0,00|
|gpt-6-luna-high|07-performance-grok|ok|22|100|5,50|0,00|8,65|8,65|
|gpt-6.1-sol-high|05-cli-claude|ok|74|100|6,00|0,00|8,80|8,80|
|gpt-6.1-sol-high|05-cli-gemini|ok|104|100|9,00|0,00|9,70|9,70|
|gpt-6.1-sol-high|08-testes-claude|ok|139|100|7,00|0,00|9,10|9,10|
|gpt-6.1-sol-high|08-testes-gemini|ok|83|100|8,00|0,00|9,40|9,40|
|gpt-6.1-sol-medium|09-api-gemini|ok|59|100|8,50|0,00|9,55|9,55|
|gpt-6.1-sol-medium|09-api-grok|ok|75|100|7,50|0,00|9,25|9,25|

## Incoerências

- Contagem conferida: 70 refeitas (opus-high 1, luna-high 1, sol-high 4, sol-medium 2, flash-high 26 [12 ok/14 timeout], flash-medium 21 [16/5], argon-high 8 [5/3], argon-medium 7 [6/1]). Bate com o Chefe. 23 timeouts de novo no Gemini.
- O processo de refação APAGOU nas pastas vivas (git status D) os 70 `avaliacao_avaliador.json` oficiais commitados e os `avaliacao.json` antigos. Estão preservados no git HEAD e nos backups `_timeouts_180s/` e `_timeouts_300s/`. Não restaurei nada.
- As refações e os novos arquivos de `codigo/` não estão commitados.
- A auditoria (resultado.json × junit.xml × testes_saida.txt × rerun em /tmp × hash dos testes ocultos) não achou divergência nas 70.

## Conclusão sobre a teoria do timeout

**EVIDÊNCIA:**
- Com 420 s, opus, luna e sol ficam com high ≥ medium ou empatados: opus +0,01, luna +0,19, sol −0,02 (era −0,31, −0,09 e −0,63).
- No argon, o high só passa o medium na versão ii (+0,08). Na versão i fica −0,57, por causa de 3 timeouts contra 1.
- O flash-high continua pior que o medium (−2,80 na i; −1,71 na ii). São 14 timeouts contra 5, e o high entrega mais devagar, em geral entre 300 e 420 s.
- Nos casos em que o high terminou, a nota é igual à do medium (cerca de 9–10).
- A teoria se confirma para Claude e Codex e, em parte, para o argon. O ranking muda: opus-high sobe de 4º para 2º, sol sobe e luna-medium cai.

**PALPITE:**
- O flash-high parece precisar de mais de 7 min, ou fica em loop. Algumas entregas parciais estão perfeitas (100% dos testes), o que sugere que o agente não para de trabalhar sozinho, e não que falte capacidade.
- 10-ambigua-claude deu timeout com 0% em todos os Gemini, o que indica um problema específico dessa tarefa.
