# Rodada 1 — resultados

528 execuções (fora piloto). Nota final (0–10) = 0,7×%testes/10 + 0,3×rubrica (média de 2 juízes neutros; se só 1 válido, a nota dele). **Nota** conta timeout como 0; **Nota s/ pen.** ignora a penalidade.

## Ranking modelo × esforço

|#|Modelo|Nota|Nota s/ pen.|%testes|Rubrica|Tempo médio (s)|Timeouts|Erros|N|
|-|-|-|-|-|-|-|-|-|-|
|1|claude-haiku-5-5-high (claude)|9.76|9.76|100.0|9.21|51|0|0|33|
|2|claude-haiku-5-5-medium (claude)|9.71|9.71|99.4|9.15|29|0|0|33|
|3|claude-opus-5-5-medium (claude)|9.68|9.68|100.0|8.92|43|0|0|33|
|4|gpt-6-luna-medium (codex)|8.96|8.96|96.8|7.30|20|0|0|33|
|5|gpt-6-luna-high (codex)|8.84|8.84|96.1|7.05|32|1|0|33|
|6|gpt-6.1-sol-medium (codex)|8.77|8.77|93.7|7.36|61|2|0|33|
|7|gpt-6.1-sol-high (codex)|7.86|8.41|91.9|6.59|88|5|0|33|
|8|claude-opus-5-5-high (claude)|7.62|7.92|81.8|7.30|42|1|7|33|
|9|gemini-4-argon-medium (gemini)|7.37|8.69|91.3|7.67|120|7|0|33|
|10|grok-4.7-build-fast-medium (grok)|7.00|8.73|91.1|7.85|110|9|0|33|
|11|gemini-4-argon-high (gemini)|6.62|8.66|91.1|7.62|138|10|0|33|
|12|grok-4.7-medium (grok)|6.40|7.95|82.0|7.36|145|11|0|33|
|13|grok-4.7-build-fast-high (grok)|3.50|5.15|54.0|4.58|172|21|0|33|
|14|gemini-3.8-flash-medium (gemini)|2.63|5.55|58.7|4.80|193|24|0|33|
|15|grok-4.7-high (grok)|1.22|1.73|18.4|1.47|101|13|16|33|
|16|gemini-3.8-flash-high (gemini)|1.19|3.22|34.6|2.67|207|29|0|33|

## Tipo × empresa (nota com penalidade)

|Tipo|claude|codex|gemini|grok|
|-|-|-|-|-|
|01-funcao|9.60|8.97|4.76|7.05|
|02-bug|9.70|9.41|6.34|7.28|
|03-refatoracao|9.69|9.52|4.07|5.58|
|04-dados|8.48|8.68|3.00|1.14|
|05-cli|8.90|7.70|4.72|5.65|
|06-multiarquivo|9.59|9.45|4.76|4.99|
|07-performance|9.59|8.29|5.36|7.14|
|08-testes|9.85|6.91|0.83|0.87|
|09-api|9.71|7.73|5.66|4.94|
|10-ambigua|7.50|9.36|6.49|4.07|

## Medium vs high

|Modelo|Medium|High|Δ|Tempo med/high (s)|
|-|-|-|-|-|
|claude-haiku-5-5|9.71|9.76|+0.06|29/51|
|claude-opus-5-5|9.68|7.62|-2.06|43/42|
|gemini-3.8-flash|2.63|1.19|-1.43|193/207|
|gemini-4-argon|7.37|6.62|-0.75|120/138|
|gpt-6-luna|8.96|8.84|-0.13|20/32|
|gpt-6.1-sol|8.77|7.86|-0.91|61/88|
|grok-4.7|6.40|1.22|-5.18|145/101|
|grok-4.7-build-fast|7.00|3.50|-3.50|110/172|

## Consistência (04-dados-claude; Claude usa 04-dados-grok; runs 1–4)

|Modelo|Notas por run|Média|Desvio|
|-|-|-|-|
|claude-haiku-5-5-high|10.0, 9.7, 9.7, 9.8|9.81|0.12|
|claude-haiku-5-5-medium|9.8, 9.8, 10.0, 10.0|9.93|0.08|
|claude-opus-5-5-high|10.0, 0.0, 0.0, 0.0|2.50|4.33|
|claude-opus-5-5-medium|9.8, 9.7, 9.8, 9.8|9.81|0.06|
|gpt-6-luna-high|8.4, 8.9, 8.9, 8.9|8.77|0.19|
|gpt-6-luna-medium|9.4, 9.1, 8.9, 9.4|9.20|0.22|
|gpt-6.1-sol-high|9.1, 9.1, 9.1, 0.0|6.82|3.94|
|gpt-6.1-sol-medium|9.1, 9.1, 9.1, 8.9|9.06|0.06|
|gemini-3.8-flash-high|0.0, 0.0, 0.0, 0.0|0.00|0.00|
|gemini-3.8-flash-medium|0.0, 0.0, 0.0, 0.0|0.00|0.00|
|gemini-4-argon-high|0.0, 8.8, 0.0, 0.0|2.20|3.81|
|gemini-4-argon-medium|8.8, 8.5, 8.8, 8.8|8.73|0.13|
|grok-4.7-build-fast-high|0.0, 0.0, 0.0, 0.0|0.00|0.00|
|grok-4.7-build-fast-medium|8.9, 0.0, 0.0, 0.0|2.24|3.88|
|grok-4.7-high|0.0, 0.0, 0.0, 0.0|0.00|0.00|
|grok-4.7-medium|0.0, 0.0, 0.0, 8.8|2.20|3.81|

## Tarefas em que todos tiraram 100% nos testes

- 01-funcao-gemini
- 02-bug-codex

Quase (≥90% das execuções com 100%): 01-funcao-codex (11/12), 02-bug-gemini (11/12), 02-bug-grok (11/12), 03-refatoracao-gemini (11/12), 06-multiarquivo-grok (11/12), 07-performance-gemini (11/12), 09-api-codex (11/12), 10-ambigua-grok (11/12)

## Divergência entre juízes

- Execuções com 2 juízes válidos: 344; com só 1: 175; com 0: 9. (sem juiz válido → rubrica 0)
- |diferença| média: 0.62 pts (de 10); mediana 0.00; >3 pts: 5.
- Falhas de juiz (tentativas): grok — JSON inválido: 212; gemini — timeout: 130; claude — JSON inválido: 66; grok — timeout: 13
- Média dada por juiz: claude 6.87 (n=211), codex 6.15 (n=276), gemini 6.97 (n=222), grok 8.56 (n=154)

## Casos com rubrica 0,0 de algum juiz

96 execuções. Todas são timeout ou erro do agente — nenhuma com status ok: timeout/código vazio: 56, timeout/código parcial: 19, erro/código vazio: 15, erro/código parcial: 6.
Ou seja, o 0 é o juiz avaliando solução vazia/incompleta, não falha do juiz. As falhas reais de juiz (JSON inválido, sobretudo do Grok build-fast e também do Claude Haiku; timeouts do Gemini Flash) aparecem como 'só 1 juiz válido' e são cobertas pelo fallback.

|Modelo|Rubrica 0|
|-|-|
|grok-4.7-high|24|
|gemini-3.8-flash-high|20|
|grok-4.7-build-fast-high|15|
|gemini-3.8-flash-medium|12|
|claude-opus-5-5-high|6|
|grok-4.7-medium|6|
|gpt-6.1-sol-high|3|
|grok-4.7-build-fast-medium|3|
|gemini-4-argon-high|3|
|gpt-6.1-sol-medium|2|
|gpt-6-luna-high|1|
|gemini-4-argon-medium|1|

## Mutation score (tipo 08)

Não foi calculado com mutmut na rodada. O tipo 08 mede a qualidade dos testes escritos pelo agente via testes ocultos que rodam a suíte contra mutantes pré-definidos (ex.: 14 mutantes em 08-testes-claude); o %testes nesse tipo funciona como proxy de mutation score.

## Ressalvas importantes

- **Os 23 erros não são falhas de capacidade, e sim de cota:** 16 em grok-4.7-high são `402 Grok Build usage balance exhausted`; 7 em claude-opus-5-5-high são `You've hit your session limit`. O ranking desses dois fica distorcido para baixo. Para comparar de verdade, essas execuções precisam ser refeitas com cota disponível.
- **Muitos timeouts (133)** com limite de 3 a 5 min por tarefa, e as execuções rodaram em paralelo (3 a 4 por empresa). Isso pesa sobretudo em Gemini Flash e Grok high. Por isso a coluna "Nota s/ pen." também aparece.
- **A máquina ficou pausada** de 20:52 a 0:54 (BRT). Os processos foram congelados e retomados depois; isso pode ter inflado alguns tempos.
- Viés dos juízes: o Grok (build-fast) dá notas mais altas (média 8,56) e devolve JSON inválido com frequência; o Codex (luna) é o mais severo (6,15).
