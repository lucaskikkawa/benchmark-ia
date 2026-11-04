# Rodada 1 — resultados (notas do avaliador)

528 execuções (16 combinações × 33). Ranking com **N=30** por combinação (as 3 repetições de consistência ficam fora da nota). Nota final (0–10) = 0,7×%testes/10 + 0,3×rubrica (média de 2 juízes neutros: nenhum da empresa resolvedora nem da autora da tarefa; código anonimizado). **Timeout = 0.** Fonte: `avaliacao_avaliador.json` em cada execução; metodologia, auditoria e comparação com as notas antigas em `RELATORIO_AVALIADOR.md`.

## Regras específicas

- **Tipo 08 (testes)**: tem mutation score: os testes ocultos rodam a suíte escrita pelo agente contra mutantes plantados (10–14 por tarefa), e o %testes é a taxa de mutantes mortos. (A versão anterior deste arquivo dizia, por engano, que o mutation score não tinha sido calculado.)
- **Correção no teste do tipo 08**: `tarefas/08-testes-grok/testes_ocultos/test_mutantes.py` concatenava texto com bytes no tratamento de timeout do mutante (`TypeError` sob carga). Corrigido só o tratamento do erro; o que o teste avalia não mudou. Reexecutado em todas as 12 execuções da 08-testes-grok: nenhuma nota do avaliador mudou (a gpt-6.1-sol-medium já contava 15/15 pela reexecução; o resultado.json original registrava 14/15).
- **grok-4.7-high** (decisão do Lucas; tempo pelo campo `duracao_agente_s` do agente): 1ª tentativa concluída em até 300 s = nota cheia; 2ª tentativa (limite 900 s) = no máximo 70%: até 600 s ×0,7; de 600 a 900 s ×0,5; acima de 900 s com entrega parcial ×0,5; sem entrega, zero. As demais execuções dele seguem a regra geral.

## Ranking modelo × esforço

|#|Modelo|Nota|%testes|Rubrica (não-timeout)|Timeouts|N|
|-|-|-|-|-|-|-|
|1|claude-haiku-5-5-high (claude)|9.75|100.00|9.18|0|30|
|2|claude-opus-5-5-medium (claude)|9.70|100.00|9.00|0|30|
|3|claude-haiku-5-5-medium (claude)|9.66|99.39|9.00|0|30|
|4|claude-opus-5-5-high (claude)|9.39|100.00|9.03|1|30|
|5|gpt-6-luna-medium (codex)|9.09|96.54|7.78|0|30|
|6|gpt-6-luna-high (codex)|9.00|95.99|7.86|1|30|
|7|gpt-6.1-sol-medium (codex)|8.79|93.33|8.05|2|30|
|8|gpt-6.1-sol-high (codex)|8.16|94.44|8.04|4|30|
|9|grok-4.7-build-fast-medium (grok)|7.68|93.53|8.67|6|30|
|10|gemini-4-argon-medium (gemini)|7.22|90.47|8.04|7|30|
|11|gemini-4-argon-high (gemini)|6.96|90.20|8.32|8|30|
|12|grok-4.7-medium (grok)|6.72|83.53|8.69|9|30|
|13|grok-4.7-build-fast-high (grok)|3.86|59.36|8.88|18|30|
|14|grok-4.7-high (grok)|3.83|50.15|7.22|17|30|
|15|gemini-3.8-flash-medium (gemini)|2.85|64.56|8.33|21|30|
|16|gemini-3.8-flash-high (gemini)|1.31|38.09|9.50|26|30|

## Por empresa

|Empresa|Nota|
|-|-|
|claude|9.62|
|codex|8.76|
|grok|5.52|
|gemini|4.58|

## Tipo × empresa

|Tipo|claude|codex|gemini|grok|
|-|-|-|-|-|
|01-funcao|9.62|9.09|4.79|7.09|
|02-bug|9.65|9.40|6.40|7.21|
|03-refatoracao|9.69|9.52|4.02|5.61|
|04-dados|9.60|9.34|3.10|1.55|
|05-cli|8.88|7.88|4.64|5.67|
|06-multiarquivo|9.61|9.44|4.62|5.63|
|07-performance|9.61|8.50|5.33|9.50|
|08-testes|9.87|7.12|0.82|1.23|
|09-api|9.74|7.90|5.61|6.33|
|10-ambigua|9.97|9.39|6.53|5.42|

## Medium vs high

|Modelo|Medium|High|Δ|
|-|-|-|-|
|claude-haiku-5-5|9.66|9.75|+0.09|
|claude-opus-5-5|9.70|9.39|-0.31|
|gemini-3.8-flash|2.85|1.31|-1.54|
|gemini-4-argon|7.22|6.96|-0.26|
|gpt-6-luna|9.09|9.00|-0.09|
|gpt-6.1-sol|8.79|8.16|-0.63|
|grok-4.7|6.72|3.83|-2.89|
|grok-4.7-build-fast|7.68|3.86|-3.82|

## Consistência (tarefa fixa 04-dados-claude; Claude usa 04-dados-grok; runs 1–4) — não entra na nota

|Modelo|Notas novas por run|Média|Desvio|Antiga média|
|-|-|-|-|-|
|claude-haiku-5-5-high|9.85, 9.85, 9.85, 9.55|9.78|0.13|9.81|
|claude-haiku-5-5-medium|9.85, 10.00, 10.00, 9.85|9.93|0.08|9.93|
|claude-opus-5-5-high|9.70, 9.70, 9.70, 9.85|9.74|0.06|9.78|
|claude-opus-5-5-medium|9.85, 9.85, 9.70, 9.85|9.81|0.06|9.81|
|gemini-3.8-flash-high|0.00, 0.00, 0.00, 0.00|0.00|0.00|0.00|
|gemini-3.8-flash-medium|0.00, 0.00, 0.00, 0.00|0.00|0.00|0.00|
|gemini-4-argon-high|0.00, 8.80, 0.00, 0.00|2.20|3.81|2.20|
|gemini-4-argon-medium|8.80, 8.95, 8.80, 8.80|8.84|0.06|8.73|
|gpt-6-luna-high|8.88, 8.73, 9.03, 8.73|8.84|0.12|8.77|
|gpt-6-luna-medium|9.25, 9.25, 9.18, 9.40|9.27|0.08|9.20|
|gpt-6.1-sol-high|9.10, 9.10, 9.10, 0.00|6.82|3.94|6.82|
|gpt-6.1-sol-medium|9.10, 9.40, 9.10, 8.95|9.14|0.16|9.06|
|grok-4.7-build-fast-high|0.00, 0.00, 0.00, 0.00|0.00|0.00|0.00|
|grok-4.7-build-fast-medium|8.95, 0.00, 0.00, 0.00|2.24|3.88|2.24|
|grok-4.7-high|0.00, 4.40, 4.70, 4.70|3.45|2.00|0.00|
|grok-4.7-medium|0.00, 0.00, 0.00, 8.95|2.24|3.88|2.20|


## Dois rankings oficiais (decisão do Lucas, 04/11/2026)

- **Ranking original**: vale para a configuração com limite de 180/300 s. É o deste relatório, com `resultados/notas_avaliador.csv`.
- **Ranking 7 min (420 s)**: as 70 run-1 que deram timeout em Claude, Codex e Gemini foram refeitas com 420 s. Fica em `resultados/_avaliador/cenario_7min/` (`RELATORIO_7MIN.md`, `notas_7min.csv`, `matriz_7min.csv`), em duas versões: **(i)** timeout = 0 e **(ii)** julgando a entrega parcial em `codigo/`.
- Nas 70 pastas refeitas, `avaliacao_avaliador.json` corresponde à execução original (180/300 s), cujos arquivos estão em `resultados/_timeouts_180s/` e `_timeouts_300s/`. Já `avaliacao_avaliador_7min.json` corresponde à execução de 420 s que está na pasta (`resultado.json`, `junit.xml`, `testes_saida.txt`, `codigo/`).
