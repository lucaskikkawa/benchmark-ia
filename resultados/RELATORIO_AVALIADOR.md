# Relatório do Avaliador — Rodada 1 (reavaliação independente)

Gerado por `scripts/avaliador.py` (rubrica), `scripts/avaliador_auditoria.py` (auditoria/reexecução) e `scripts/avaliador_relatorio.py`. As avaliações antigas (`avaliacao.json`, `RODADA.md`) não foram alteradas; as novas estão em `avaliacao_avaliador.json` em cada `run-N`. Aprovado pelo Lucas; `RODADA.md` foi regenerado a partir destas notas.

## Metodologia

- **Nota (0–10)** = 0,7 × (%testes/10) + 0,3 × rubrica(0–10). Mesma escala do `julgar.py`/`RODADA.md`. **Timeout = 0** (rubrica nem é julgada).
- **Rubrica**: 5 itens de 0 a 2 do `rubrica.yaml` de cada tarefa; avalia o código entregue. Tipo 10: o item de documentação confere o `SUPOSICOES.md`. Tipo 08: o %testes é a taxa de mutantes mortos (os testes ocultos rodam a suíte do agente contra os mutantes plantados, 10–14 por tarefa).
- **Juízes**: 2 por solução, média simples. Nenhum juiz é da empresa resolvedora nem da autora da tarefa (plano §6), então os 2 juízes são exatamente as 2 empresas restantes. Motores: Anthropic=`claude` (claude-haiku-5-5), OpenAI=`codex` (gpt-6-luna), Google=`agy` (gemini-3.8-flash), xAI=`grok` (grok-4.7-build-fast), todos esforço medium, os mesmos modelos de juiz do `julgar.py` para comparabilidade. Se um juiz falha 2 vezes, vale só o outro (registrado em `obs`).
- **Anonimização**: código sem `enunciado.md`; nomes de modelo/empresa trocados por `[anon]`, linhas de autoria e caminhos absolutos removidos; juiz chamado fora da pasta, sem ferramentas de escrita.
- **Escopo**: 16 combinações × 33 = 528 execuções (grok-4.7-high com regras excepcionais em 13 delas). A nota/ranking usa só as 30 execuções principais (run-1); as runs 2–4 da tarefa de consistência só medem variação. Obs.: o `RODADA.md` antigo usa N=33 (inclui as repetições) — por isso a comparação abaixo mostra também a nota antiga recalculada nas mesmas 30 execuções.
- **grok-4.7-high**: 13 execuções refeitas seguem regra excepcional de tempo (1ª tentativa ≤300 s: nota cheia; 2ª tentativa de 900 s: máx. 70% — ≤600 s ×0,7, 600–900 s ×0,5, >900 s parcial ×0,5, sem entrega 0); detalhes na seção própria.
- **Auditoria**: para cada execução, conferidos resultado.json × junit.xml × resumo do testes_saida.txt; caminho × campos; status × duração × timeout; arquivos de solução; hash dos testes_ocultos atuais × HEAD do git; mudanças não commitadas; histórico git do resultado.json; fórmula e juízes do avaliacao.json antigo; e **reexecução dos testes ocultos** sobre o código entregue (495/495).

## Ranking novo por modelo × esforço (30 execuções principais)

|#|Modelo|Empresa|Nota nova|Antiga (mesmas 30)|Δ|Antiga RODADA.md (33)|%testes|Rubrica nova (só não-timeout)|Timeouts|N|
|-|-|-|-|-|-|-|-|-|-|-|
|1|claude-haiku-5-5-high|claude|**9.75**|9.77|-0.02|9.76|100.00|9.18|0|30|
|2|claude-opus-5-5-medium|claude|**9.70**|9.66|+0.04|9.68|100.00|9.00|0|30|
|3|claude-haiku-5-5-medium|claude|**9.66**|9.68|-0.02|9.71|99.39|9.00|0|30|
|4|claude-opus-5-5-high|claude|**9.39**|9.38|+0.01|9.41|100.00|9.03|1|30|
|5|gpt-6-luna-medium|codex|**9.09**|8.95|+0.14|8.96|96.54|7.78|0|30|
|6|gpt-6-luna-high|codex|**9.00**|8.83|+0.17|8.84|95.99|7.86|1|30|
|7|gpt-6.1-sol-medium|codex|**8.79**|8.74|+0.05|8.77|93.33|8.05|2|30|
|8|gpt-6.1-sol-high|codex|**8.16**|8.04|+0.12|7.86|94.44|8.04|4|30|
|9|grok-4.7-build-fast-medium|grok|**7.68**|7.70|-0.02|7.00|93.53|8.67|6|30|
|10|gemini-4-argon-medium|gemini|**7.22**|7.24|-0.02|7.37|90.47|8.04|7|30|
|11|gemini-4-argon-high|gemini|**6.96**|6.99|-0.03|6.62|90.20|8.32|8|30|
|12|grok-4.7-medium|grok|**6.72**|6.75|-0.03|6.40|83.53|8.69|9|30|
|13|grok-4.7-build-fast-high|grok|**3.86**|3.85|+0.01|3.50|59.36|8.88|18|30|
|14|grok-4.7-high|grok|**3.83**|2.26|+1.57|2.05|50.15|7.22|17|30|
|15|gemini-3.8-flash-medium|gemini|**2.85**|2.89|-0.04|2.63|64.56|8.33|21|30|
|16|gemini-3.8-flash-high|gemini|**1.31**|1.31|+0.00|1.19|38.09|9.50|26|30|

## Ranking por empresa (média das combinações)

|Empresa|Nota nova|Antiga (30)|Δ|
|-|-|-|-|
|claude|9.62|9.62|+0.00|
|codex|8.76|8.64|+0.12|
|grok|5.52|5.14|+0.38|
|gemini|4.58|4.61|-0.03|

## Tipo × empresa resolvedora (nota nova; antiga entre parênteses)

|Tipo|claude|codex|gemini|grok|
|-|-|-|-|-|
|01-funcao|9.62 (9.60)|9.09 (8.97)|4.79 (4.76)|7.09 (7.05)|
|02-bug|9.65 (9.70)|9.40 (9.41)|6.40 (6.34)|7.21 (7.28)|
|03-refatoracao|9.69 (9.69)|9.52 (9.52)|4.02 (4.07)|5.61 (5.58)|
|04-dados|9.60 (9.59)|9.34 (9.07)|3.10 (3.08)|1.55 (1.55)|
|05-cli|8.88 (8.90)|7.88 (7.70)|4.64 (4.72)|5.67 (5.65)|
|06-multiarquivo|9.61 (9.59)|9.44 (9.45)|4.62 (4.76)|5.63 (4.86)|
|07-performance|9.61 (9.59)|8.50 (8.29)|5.33 (5.36)|9.50 (8.78)|
|08-testes|9.87 (9.85)|7.12 (6.91)|0.82 (0.83)|1.23 (0.83)|
|09-api|9.74 (9.72)|7.90 (7.73)|5.61 (5.66)|6.33 (4.94)|
|10-ambigua|9.97 (10.00)|9.39 (9.36)|6.53 (6.49)|5.42 (4.88)|

## Por tarefa (média das combinações que a resolveram)

|Tarefa|N|Nota nova|Antiga|Δ|%testes|Timeouts|
|-|-|-|-|-|-|-|
|01-funcao-claude|12|4.36|4.40|-0.04|74.28|6|
|01-funcao-codex|12|8.97|8.93|+0.04|91.67|1|
|01-funcao-gemini|12|9.57|9.55|+0.02|100.00|0|
|01-funcao-grok|12|7.68|7.51|+0.17|83.33|2|
|02-bug-claude|12|7.06|7.04|+0.02|87.82|3|
|02-bug-codex|12|10.00|10.00|+0.00|100.00|0|
|02-bug-gemini|12|7.83|7.91|-0.08|92.08|2|
|02-bug-grok|12|7.77|7.78|-0.01|92.71|2|
|03-refatoracao-claude|12|4.64|4.66|-0.02|91.41|6|
|03-refatoracao-codex|12|8.07|8.10|-0.03|91.23|2|
|03-refatoracao-gemini|12|8.11|8.08|+0.03|91.67|2|
|03-refatoracao-grok|12|8.01|8.02|-0.01|95.83|2|
|04-dados-claude|12|4.51|4.48|+0.03|66.41|6|
|04-dados-codex|12|3.94|3.92|+0.02|66.67|7|
|04-dados-gemini|12|7.06|7.00|+0.06|75.00|3|
|04-dados-grok|12|8.08|7.90|+0.18|83.33|2|
|05-cli-claude|12|6.97|7.00|-0.03|83.33|3|
|05-cli-codex|12|6.47|6.47|+0.00|75.00|4|
|05-cli-gemini|12|6.45|6.48|-0.03|87.88|4|
|05-cli-grok|12|7.17|7.03|+0.14|84.44|3|
|06-multiarquivo-claude|12|5.43|5.68|-0.25|83.33|5|
|06-multiarquivo-codex|12|8.11|7.30|+0.81|91.86|2|
|06-multiarquivo-gemini|12|8.12|8.13|-0.01|83.33|2|
|06-multiarquivo-grok|12|7.64|7.55|+0.09|99.02|2|
|07-performance-claude|12|7.60|6.67|+0.93|91.67|2|
|07-performance-codex|12|8.89|8.90|-0.01|91.67|1|
|07-performance-gemini|12|9.65|9.64|+0.01|100.00|0|
|07-performance-grok|12|6.81|6.80|+0.01|75.00|3|
|08-testes-claude|12|1.70|1.73|-0.03|22.06|9|
|08-testes-codex|12|4.51|4.13|+0.38|74.44|6|
|08-testes-gemini|12|5.51|5.49|+0.02|74.36|5|
|08-testes-grok|12|7.32|7.08|+0.24|98.89|3|
|09-api-claude|12|5.62|5.45|+0.17|75.00|5|
|09-api-codex|12|8.74|8.16|+0.58|100.00|1|
|09-api-gemini|12|8.13|7.32|+0.81|91.67|2|
|09-api-grok|12|7.08|7.12|-0.04|83.33|3|
|10-ambigua-claude|12|3.08|3.13|-0.05|32.54|8|
|10-ambigua-codex|12|9.95|9.95|+0.00|100.00|0|
|10-ambigua-gemini|12|8.57|8.00|+0.57|91.67|1|
|10-ambigua-grok|12|9.72|9.65|+0.07|100.00|0|

Matriz completa modelo × tarefa (nota antiga e nova por execução): `resultados/_avaliador/notas_avaliador.csv`.

### Maiores diferenças por execução

|Execução|Antiga|Nova|Δ|Motivo provável|
|-|-|-|-|-|
|grok/grok-4.7-high/09-api-gemini/run-1|0.00|10.00|+10.00|rubrica|
|grok/grok-4.7-high/06-multiarquivo-codex/run-1|0.00|9.70|+9.70|rubrica|
|grok/grok-4.7-high/07-performance-claude/run-1|0.00|8.65|+8.65|rubrica|
|grok/grok-4.7-high/09-api-codex/run-1|0.00|7.00|+7.00|antiga sem juiz válido (rubrica 0)|
|grok/grok-4.7-high/10-ambigua-gemini/run-1|0.00|6.58|+6.58|antiga sem juiz válido (rubrica 0)|
|grok/grok-4.7-high/08-testes-codex/run-1|0.00|4.92|+4.92|antiga sem juiz válido (rubrica 0)|
|codex/gpt-6-luna-medium/04-dados-grok/run-1|7.00|9.55|+2.55|antiga sem juiz válido (rubrica 0)|
|codex/gpt-6.1-sol-high/07-performance-claude/run-1|7.00|9.40|+2.40|antiga sem juiz válido (rubrica 0)|
|codex/gpt-6-luna-medium/05-cli-grok/run-1|7.00|9.25|+2.25|antiga sem juiz válido (rubrica 0)|
|codex/gpt-6-luna-high/08-testes-grok/run-1|6.53|8.78|+2.25|antiga sem juiz válido (rubrica 0)|
|codex/gpt-6-luna-high/09-api-claude/run-1|7.00|9.10|+2.10|antiga sem juiz válido (rubrica 0)|
|codex/gpt-6-luna-medium/01-funcao-grok/run-1|7.00|8.95|+1.95|antiga sem juiz válido (rubrica 0)|

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

## Juízes

- Execuções julgadas: 390 (timeouts não julgados: 138). Com 2 juízes válidos: 394; com só 1: 0; com 0: 0.
- |diferença| média entre juízes: 0.63 pts; >3 pts: 3.
- claude: média 8.28 (n=175), falhas definitivas 0.
- codex: média 8.40 (n=174), falhas definitivas 0.
- gemini: média 8.34 (n=232), falhas definitivas 0.
- grok: média 8.60 (n=207), falhas definitivas 0.

## Incoerências encontradas

**Pipeline/código:**
- `runner/run.py` e `scripts/rodada.py` têm mudanças **não commitadas** (override `BENCH_TIMEOUT_S` até 900 s e campo `timeout_s` no resultado.json). As 495 execuções avaliadas aqui não têm `timeout_s` (geradas antes); só as refeitas do grok-4.7-high terão — o timeout delas não é o mesmo das demais.
- `resultados/_timeouts_180s/` e `_timeouts_300s/` e `scripts/relatorio.py`, `site/` não estão versionados.
- Plano §5 fala em 5 min padrão, mas todas as tarefas usam `timeout_min` do meta.yaml (ex.: 3 min em 04-dados-claude), o que explica boa parte dos timeouts do Gemini Flash e Grok high.
- `RODADA.md` antigo: ranking com N=33 (inclui as 3 repetições de consistência, dando peso 4× à tarefa 04-dados) e execuções sem juiz válido entram com rubrica 0 (9 casos) em vez de ficarem pendentes.
- `RODADA.md` antigo dizia que o mutation score do tipo 08 não foi calculado; na prática os testes ocultos do tipo 08 já são mutation testing com mutantes plantados — o %testes é a taxa de mortos. Corrigido no `RODADA.md` regenerado.
- Harness `tarefas/08-testes-grok/testes_ocultos/test_mutantes.py`: no `except subprocess.TimeoutExpired` faz `(exc.stdout or "") + (exc.stderr or "")`, mas com `text=True` o `TimeoutExpired` traz bytes → `TypeError`. Sob carga (mutante >45 s) o teste falha por bug do harness, não do agente. **Corrigido** (só o tratamento do erro: decodifica bytes antes de concatenar; o que o teste avalia não mudou) e reexecutado nas 12 execuções da 08-testes-grok (grok não resolve tarefa própria): nenhuma contagem mudou em relação às notas do avaliador; a única afetada (gpt-6.1-sol-medium, 14/15 no resultado.json original) já usava 15/15 da reexecução. Detalhes em `resultados/_avaliador/rerun_08_testes_grok.json`.
- Testes ocultos atuais: hash idêntico ao HEAD do git em todas as 40 tarefas; último commit em `tarefas/` (67ae40f, 29/10 19:05) é anterior ao início da rodada (19:07) — **nenhuma alteração de teste detectada**. Nenhum `codigo/` contém `testes_ocultos`.
- Nenhum `resultado.json` diverge do `junit.xml` nem do resumo do `testes_saida.txt`; nenhuma `nota_final_10` antiga diverge da fórmula; nenhum juiz antigo não-neutro; nenhuma execução de tarefa da própria empresa. **Sem indício de edição manual de nota/resultado.**

- **Arquivos não rastreados em resultados/ (pergunta do Bench - Grok)**: o avaliador **não criou nenhuma pasta de execução nova** (claude, codex ou outra). `git status --untracked-files=all` não mostra nenhuma pasta `run-N` nova fora do grok-4.7-high; os únicos arquivos não rastreados em `resultados/claude/` e `resultados/codex/` (e gemini/grok) são os `avaliacao_avaliador.json` criados por este avaliador, um por `run-N` — provavelmente o que foi visto. As reexecuções de testes rodam em cópias em /tmp e não gravam nada nas pastas.
- grok-4.7-high: `04-dados-claude/run-2` e `run-3` aparecem como modificados (M) no git e os `avaliacao.json` antigos foram apagados (D) pela nova execução do Bench - Grok (versões antigas preservadas no HEAD do git e em `_erros_cota/`, `_timeouts_180s/`, `_timeouts_300s/`). As novas execuções têm `timeout_s` 300 ou 900, diferente dos 180 s/300 s da rodada original — assimetria de regras já conhecida.

**Por execução:**

- resultado.json da rodada sobrescreveu o do piloto (commit 98a25b8 'Piloto') no mesmo caminho run-1; o piloto está em resultados/piloto. Benigno, mas o histórico do arquivo mistura duas execuções — 16: `claude/claude-haiku-5-5-high/01-funcao-codex/run-1`; `claude/claude-haiku-5-5-medium/01-funcao-codex/run-1`; `claude/claude-opus-5-5-high/01-funcao-codex/run-1`; `claude/claude-opus-5-5-medium/01-funcao-codex/run-1`; `codex/gpt-6-luna-high/01-funcao-claude/run-1`; `codex/gpt-6-luna-medium/01-funcao-claude/run-1`; `codex/gpt-6.1-sol-high/01-funcao-claude/run-1`; `codex/gpt-6.1-sol-medium/01-funcao-claude/run-1`; `gemini/gemini-3.8-flash-high/01-funcao-codex/run-1`; `gemini/gemini-3.8-flash-medium/01-funcao-codex/run-1`; `gemini/gemini-4-argon-high/01-funcao-codex/run-1`; `gemini/gemini-4-argon-medium/01-funcao-codex/run-1`; `grok/grok-4.7-build-fast-high/01-funcao-codex/run-1`; `grok/grok-4.7-build-fast-medium/01-funcao-codex/run-1`; `grok/grok-4.7-high/01-funcao-codex/run-1`; `grok/grok-4.7-medium/01-funcao-codex/run-1`
- execução refeita (commit b850e82 'Refaz 7 execuções do opus-5-5-high que falharam por cota'; backup em resultados/_erros_cota). Documentada no commit — 7: `claude/claude-opus-5-5-high/04-dados-grok/run-2`; `claude/claude-opus-5-5-high/04-dados-grok/run-3`; `claude/claude-opus-5-5-high/04-dados-grok/run-4`; `claude/claude-opus-5-5-high/09-api-grok/run-1`; `claude/claude-opus-5-5-high/10-ambigua-codex/run-1`; `claude/claude-opus-5-5-high/10-ambigua-gemini/run-1`; `claude/claude-opus-5-5-high/10-ambigua-grok/run-1`
- 71 execuções com **timeout mas com entrega parcial que passa testes** (nota 0 pela regra; o grok-4.7-high terá regra diferente, o que cria assimetria): claude/claude-opus-5-5-high/05-cli-gemini/run-1 (22/22 testes passam (100%)); codex/gpt-6.1-sol-high/05-cli-claude/run-1 (27/27 testes passam (100%)); codex/gpt-6.1-sol-high/05-cli-gemini/run-1 (6/22 testes passam (27%)); codex/gpt-6.1-sol-high/08-testes-claude/run-1 (1/17 testes passam (6%)); codex/gpt-6.1-sol-high/08-testes-gemini/run-1 (13/13 testes passam (100%)); gemini/gemini-3.8-flash-high/02-bug-claude/run-1 (7/26 testes passam (27%)); gemini/gemini-3.8-flash-high/02-bug-grok/run-1 (2/16 testes passam (12%)); gemini/gemini-3.8-flash-high/03-refatoracao-claude/run-1 (24/32 testes passam (75%)); gemini/gemini-3.8-flash-high/03-refatoracao-codex/run-1 (9/19 testes passam (47%)); gemini/gemini-3.8-flash-high/03-refatoracao-grok/run-1 (9/12 testes passam (75%)); gemini/gemini-3.8-flash-high/05-cli-grok/run-1 (1/15 testes passam (7%)); gemini/gemini-3.8-flash-high/06-multiarquivo-codex/run-1 (42/42 testes passam (100%)); gemini/gemini-3.8-flash-high/06-multiarquivo-grok/run-1 (17/17 testes passam (100%)); gemini/gemini-3.8-flash-high/07-performance-claude/run-1 (36/36 testes passam (100%)); gemini/gemini-3.8-flash-high/08-testes-claude/run-1 (1/17 testes passam (6%)); gemini/gemini-3.8-flash-high/08-testes-grok/run-1 (14/15 testes passam (93%)); gemini/gemini-3.8-flash-high/09-api-codex/run-1 (38/38 testes passam (100%)); gemini/gemini-3.8-flash-medium/01-funcao-claude/run-1 (23/23 testes passam (100%)); gemini/gemini-3.8-flash-medium/02-bug-claude/run-1 (7/26 testes passam (27%)); gemini/gemini-3.8-flash-medium/02-bug-grok/run-1 (16/16 testes passam (100%)); gemini/gemini-3.8-flash-medium/03-refatoracao-claude/run-1 (24/32 testes passam (75%)); gemini/gemini-3.8-flash-medium/03-refatoracao-codex/run-1 (9/19 testes passam (47%)); gemini/gemini-3.8-flash-medium/03-refatoracao-grok/run-1 (9/12 testes passam (75%)); gemini/gemini-3.8-flash-medium/04-dados-codex/run-1 (47/47 testes passam (100%)); gemini/gemini-3.8-flash-medium/05-cli-codex/run-1 (28/28 testes passam (100%)); gemini/gemini-3.8-flash-medium/05-cli-grok/run-1 (1/15 testes passam (7%)); gemini/gemini-3.8-flash-medium/06-multiarquivo-grok/run-1 (17/17 testes passam (100%)); gemini/gemini-3.8-flash-medium/08-testes-claude/run-1 (1/17 testes passam (6%)); gemini/gemini-3.8-flash-medium/08-testes-grok/run-1 (15/15 testes passam (100%)); gemini/gemini-3.8-flash-medium/09-api-claude/run-1 (42/42 testes passam (100%)); gemini/gemini-3.8-flash-medium/09-api-grok/run-1 (18/18 testes passam (100%)); gemini/gemini-4-argon-high/03-refatoracao-claude/run-1 (32/32 testes passam (100%)); gemini/gemini-4-argon-high/04-dados-claude/run-1 (32/32 testes passam (100%)); gemini/gemini-4-argon-high/04-dados-claude/run-3 (32/32 testes passam (100%)); gemini/gemini-4-argon-high/04-dados-claude/run-4 (32/32 testes passam (100%)); gemini/gemini-4-argon-high/04-dados-codex/run-1 (47/47 testes passam (100%)); gemini/gemini-4-argon-high/08-testes-claude/run-1 (1/17 testes passam (6%)); gemini/gemini-4-argon-high/08-testes-codex/run-1 (15/15 testes passam (100%)); gemini/gemini-4-argon-high/08-testes-grok/run-1 (15/15 testes passam (100%)); gemini/gemini-4-argon-medium/01-funcao-claude/run-1 (23/23 testes passam (100%)); gemini/gemini-4-argon-medium/05-cli-grok/run-1 (15/15 testes passam (100%)); gemini/gemini-4-argon-medium/06-multiarquivo-claude/run-1 (40/40 testes passam (100%)); gemini/gemini-4-argon-medium/06-multiarquivo-codex/run-1 (1/42 testes passam (2%)); gemini/gemini-4-argon-medium/08-testes-claude/run-1 (2/17 testes passam (12%)); gemini/gemini-4-argon-medium/08-testes-codex/run-1 (15/15 testes passam (100%)); grok/grok-4.7-build-fast-high/02-bug-claude/run-1 (26/26 testes passam (100%)); grok/grok-4.7-build-fast-high/02-bug-gemini/run-1 (20/20 testes passam (100%)); grok/grok-4.7-build-fast-high/03-refatoracao-claude/run-1 (24/32 testes passam (75%)); grok/grok-4.7-build-fast-high/05-cli-gemini/run-1 (22/22 testes passam (100%)); grok/grok-4.7-build-fast-high/06-multiarquivo-claude/run-1 (40/40 testes passam (100%)); grok/grok-4.7-build-fast-high/08-testes-claude/run-1 (1/17 testes passam (6%)); grok/grok-4.7-build-fast-high/09-api-gemini/run-1 (46/46 testes passam (100%)); grok/grok-4.7-build-fast-medium/03-refatoracao-claude/run-1 (32/32 testes passam (100%)); grok/grok-4.7-build-fast-medium/04-dados-claude/run-2 (32/32 testes passam (100%)); grok/grok-4.7-build-fast-medium/04-dados-claude/run-4 (32/32 testes passam (100%)); grok/grok-4.7-build-fast-medium/04-dados-codex/run-1 (47/47 testes passam (100%)); grok/grok-4.7-build-fast-medium/08-testes-claude/run-1 (1/17 testes passam (6%)); grok/grok-4.7-build-fast-medium/08-testes-codex/run-1 (15/15 testes passam (100%)); grok/grok-4.7-build-fast-medium/08-testes-gemini/run-1 (13/13 testes passam (100%)); grok/grok-4.7-high/01-funcao-claude/run-1 (21/23 testes passam (91%)); grok/grok-4.7-high/02-bug-gemini/run-1 (1/20 testes passam (5%)); grok/grok-4.7-high/03-refatoracao-claude/run-1 (24/32 testes passam (75%)); grok/grok-4.7-high/04-dados-claude/run-3 (32/32 testes passam (100%)); grok/grok-4.7-high/05-cli-gemini/run-1 (6/22 testes passam (27%)); grok/grok-4.7-high/08-testes-claude/run-1 (1/17 testes passam (6%)); grok/grok-4.7-medium/03-refatoracao-gemini/run-1 (24/24 testes passam (100%)); grok/grok-4.7-medium/04-dados-claude/run-1 (32/32 testes passam (100%)); grok/grok-4.7-medium/04-dados-claude/run-2 (32/32 testes passam (100%)); grok/grok-4.7-medium/06-multiarquivo-claude/run-1 (40/40 testes passam (100%)); grok/grok-4.7-medium/08-testes-claude/run-1 (1/17 testes passam (6%)); grok/grok-4.7-medium/09-api-claude/run-1 (42/42 testes passam (100%))
- reexecução dos testes deu 15/15, resultado.json diz 14/15 — 1: `codex/gpt-6.1-sol-medium/08-testes-grok/run-1`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/04-dados-claude/run-2/agente_stdout.txt', ' D resultados/grok/grok-4.7-high/04-dados-claude/run-2/avaliacao.json', ' M resultados/grok/grok-4.7-high/04-dados-claude/run-2/junit.xml', ' M resultados/grok/grok-4.7-high/04-dados-claude/run-2/resultado.json', ' M resultados/grok/grok-4.7-high/04-dados-claude/run-2/testes_saida.txt'] — 1: `grok/grok-4.7-high/04-dados-claude/run-2`
- resultado.json alterado em 2 commits: ['b4386c7 rodada-1: refaz 16 execuções grok-4.7-high (erro de cota), julga e regenera RODADA.md', '652b466 Rodada 1: 528 execuções, avaliações e RODADA.md'] — 16: `grok/grok-4.7-high/04-dados-claude/run-2`; `grok/grok-4.7-high/04-dados-claude/run-3`; `grok/grok-4.7-high/04-dados-claude/run-4`; `grok/grok-4.7-high/06-multiarquivo-codex/run-1`; `grok/grok-4.7-high/07-performance-claude/run-1`; `grok/grok-4.7-high/07-performance-codex/run-1`; `grok/grok-4.7-high/07-performance-gemini/run-1`; `grok/grok-4.7-high/08-testes-claude/run-1`; `grok/grok-4.7-high/08-testes-codex/run-1`; `grok/grok-4.7-high/08-testes-gemini/run-1`; `grok/grok-4.7-high/09-api-claude/run-1`; `grok/grok-4.7-high/09-api-codex/run-1`; `grok/grok-4.7-high/09-api-gemini/run-1`; `grok/grok-4.7-high/10-ambigua-claude/run-1`; `grok/grok-4.7-high/10-ambigua-codex/run-1`; `grok/grok-4.7-high/10-ambigua-gemini/run-1`
- sem avaliacao.json antiga — 10: `grok/grok-4.7-high/04-dados-claude/run-2`; `grok/grok-4.7-high/04-dados-claude/run-3`; `grok/grok-4.7-high/04-dados-claude/run-4`; `grok/grok-4.7-high/08-testes-claude/run-1`; `grok/grok-4.7-high/08-testes-codex/run-1`; `grok/grok-4.7-high/08-testes-gemini/run-1`; `grok/grok-4.7-high/09-api-claude/run-1`; `grok/grok-4.7-high/09-api-codex/run-1`; `grok/grok-4.7-high/10-ambigua-claude/run-1`; `grok/grok-4.7-high/10-ambigua-gemini/run-1`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/04-dados-claude/run-3/agente_stdout.txt', ' D resultados/grok/grok-4.7-high/04-dados-claude/run-3/avaliacao.json', ' M resultados/grok/grok-4.7-high/04-dados-claude/run-3/junit.xml', ' M resultados/grok/grok-4.7-high/04-dados-claude/run-3/resultado.json', ' M resultados/grok/grok-4.7-high/04-dados-claude/run-3/testes_saida.txt'] — 1: `grok/grok-4.7-high/04-dados-claude/run-3`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/04-dados-claude/run-4/agente_stdout.txt', ' D resultados/grok/grok-4.7-high/04-dados-claude/run-4/avaliacao.json', ' M resultados/grok/grok-4.7-high/04-dados-claude/run-4/junit.xml', ' M resultados/grok/grok-4.7-high/04-dados-claude/run-4/resultado.json', ' M resultados/grok/grok-4.7-high/04-dados-claude/run-4/testes_saida.txt'] — 1: `grok/grok-4.7-high/04-dados-claude/run-4`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/06-multiarquivo-codex/run-1/agente_stdout.txt', ' M resultados/grok/grok-4.7-high/06-multiarquivo-codex/run-1/avaliacao.json', ' M resultados/grok/grok-4.7-high/06-multiarquivo-codex/run-1/codigo/estoque/modelos.py', ' M resultados/grok/grok-4.7-high/06-multiarquivo-codex/run-1/codigo/estoque/operacoes.py', ' M resultados/grok/grok-4.7-high/06-multiarquivo-codex/run-1/codigo/estoque/persistencia.py'] — 1: `grok/grok-4.7-high/06-multiarquivo-codex/run-1`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/07-performance-claude/run-1/agente_stdout.txt', ' M resultados/grok/grok-4.7-high/07-performance-claude/run-1/avaliacao.json', ' M resultados/grok/grok-4.7-high/07-performance-claude/run-1/junit.xml', ' M resultados/grok/grok-4.7-high/07-performance-claude/run-1/resultado.json', ' M resultados/grok/grok-4.7-high/07-performance-claude/run-1/testes_saida.txt'] — 1: `grok/grok-4.7-high/07-performance-claude/run-1`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/08-testes-claude/run-1/agente_stdout.txt', ' D resultados/grok/grok-4.7-high/08-testes-claude/run-1/avaliacao.json', ' M resultados/grok/grok-4.7-high/08-testes-claude/run-1/junit.xml', ' M resultados/grok/grok-4.7-high/08-testes-claude/run-1/resultado.json', ' M resultados/grok/grok-4.7-high/08-testes-claude/run-1/testes_saida.txt'] — 1: `grok/grok-4.7-high/08-testes-claude/run-1`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/08-testes-codex/run-1/agente_stdout.txt', ' D resultados/grok/grok-4.7-high/08-testes-codex/run-1/avaliacao.json', ' M resultados/grok/grok-4.7-high/08-testes-codex/run-1/junit.xml', ' M resultados/grok/grok-4.7-high/08-testes-codex/run-1/resultado.json', ' M resultados/grok/grok-4.7-high/08-testes-codex/run-1/testes_saida.txt'] — 1: `grok/grok-4.7-high/08-testes-codex/run-1`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/08-testes-gemini/run-1/agente_stdout.txt', ' D resultados/grok/grok-4.7-high/08-testes-gemini/run-1/avaliacao.json', ' M resultados/grok/grok-4.7-high/08-testes-gemini/run-1/junit.xml', ' M resultados/grok/grok-4.7-high/08-testes-gemini/run-1/resultado.json', ' M resultados/grok/grok-4.7-high/08-testes-gemini/run-1/testes_saida.txt'] — 1: `grok/grok-4.7-high/08-testes-gemini/run-1`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/09-api-claude/run-1/agente_stdout.txt', ' D resultados/grok/grok-4.7-high/09-api-claude/run-1/avaliacao.json', ' M resultados/grok/grok-4.7-high/09-api-claude/run-1/junit.xml', ' M resultados/grok/grok-4.7-high/09-api-claude/run-1/resultado.json', ' M resultados/grok/grok-4.7-high/09-api-claude/run-1/testes_saida.txt'] — 1: `grok/grok-4.7-high/09-api-claude/run-1`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/09-api-codex/run-1/agente_stdout.txt', ' D resultados/grok/grok-4.7-high/09-api-codex/run-1/avaliacao.json', ' M resultados/grok/grok-4.7-high/09-api-codex/run-1/codigo/cliente.py', ' M resultados/grok/grok-4.7-high/09-api-codex/run-1/junit.xml', ' M resultados/grok/grok-4.7-high/09-api-codex/run-1/resultado.json'] — 1: `grok/grok-4.7-high/09-api-codex/run-1`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/09-api-gemini/run-1/agente_stdout.txt', ' M resultados/grok/grok-4.7-high/09-api-gemini/run-1/avaliacao.json', ' M resultados/grok/grok-4.7-high/09-api-gemini/run-1/codigo/cliente_resiliente.py', ' M resultados/grok/grok-4.7-high/09-api-gemini/run-1/junit.xml', ' M resultados/grok/grok-4.7-high/09-api-gemini/run-1/resultado.json'] — 1: `grok/grok-4.7-high/09-api-gemini/run-1`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/10-ambigua-claude/run-1/agente_stdout.txt', ' D resultados/grok/grok-4.7-high/10-ambigua-claude/run-1/avaliacao.json', ' M resultados/grok/grok-4.7-high/10-ambigua-claude/run-1/junit.xml', ' M resultados/grok/grok-4.7-high/10-ambigua-claude/run-1/resultado.json', ' M resultados/grok/grok-4.7-high/10-ambigua-claude/run-1/testes_saida.txt'] — 1: `grok/grok-4.7-high/10-ambigua-claude/run-1`
- arquivos da execução com mudanças não commitadas: ['M resultados/grok/grok-4.7-high/10-ambigua-gemini/run-1/agente_stdout.txt', ' D resultados/grok/grok-4.7-high/10-ambigua-gemini/run-1/avaliacao.json', ' M resultados/grok/grok-4.7-high/10-ambigua-gemini/run-1/junit.xml', ' M resultados/grok/grok-4.7-high/10-ambigua-gemini/run-1/resultado.json', ' M resultados/grok/grok-4.7-high/10-ambigua-gemini/run-1/testes_saida.txt'] — 1: `grok/grok-4.7-high/10-ambigua-gemini/run-1`

## grok-4.7-high — regras excepcionais

Regras excepcionais (decisão do Lucas), tempo pelo campo `duracao_agente_s` do agente, aplicadas sobre a nota normal (0,7×%testes + 0,3×rubrica):
- 1ª tentativa (limite 300 s), concluída em até 300 s — 07-performance-claude, 06-multiarquivo-codex, 09-api-gemini: **nota cheia**.
- 2ª tentativa (limite 900 s) — **teto de 70% mesmo se terminou em menos de 300 s**: até 600 s ×0,7; 600–900 s ×0,5; acima de 900 s com entrega parcial (avalia só o que está em `codigo/`) ×0,5; sem entrega (codigo/ igual ao inicial) = 0.
- As outras 20 execuções do grok-4.7-high (rodada original/refeitas por cota) seguem a regra geral (timeout = 0).

|Execução|Status|Duração (s)|%testes|Rubrica|Nota base|Regra|Nota final|
|-|-|-|-|-|-|-|-|
|04-dados-claude/run-2|ok|649|100|6.00|8.80|2ª tentativa, 649 s (600–900 s): ×0,5|**4.40**|
|04-dados-claude/run-3|timeout|900|100|8.00|9.40|estourou 900 s (900 s): entrega incompleta avaliada, ×0,5|**4.70**|
|04-dados-claude/run-4|ok|863|100|8.00|9.40|2ª tentativa, 863 s (600–900 s): ×0,5|**4.70**|
|06-multiarquivo-codex/run-1|ok|298|100|9.00|9.70|1ª tentativa, 298 s (≤300 s): nota cheia|**9.70**|
|07-performance-claude/run-1|ok|250|100|5.50|8.65|1ª tentativa, 250 s (≤300 s): nota cheia|**8.65**|
|08-testes-claude/run-1|timeout|900|6|0.00|0.41|sem entrega (codigo/ igual ao inicial): zero|**0.00**|
|08-testes-codex/run-1|ok|862|100|9.50|9.85|2ª tentativa, 862 s (600–900 s): ×0,5|**4.92**|
|08-testes-gemini/run-1|timeout|900|0|0.00|0.00|sem entrega (codigo/ igual ao inicial): zero|**0.00**|
|09-api-claude/run-1|timeout|900|0|0.00|0.00|sem entrega (codigo/ igual ao inicial): zero|**0.00**|
|09-api-codex/run-1|ok|183|100|10.00|10.00|2ª tentativa, 183 s (≤600 s): ×0,7|**7.00**|
|09-api-gemini/run-1|ok|195|100|10.00|10.00|1ª tentativa, 195 s (≤300 s): nota cheia|**10.00**|
|10-ambigua-claude/run-1|timeout|900|0|—|0.00|sem entrega (codigo/ igual ao inicial): zero|**0.00**|
|10-ambigua-gemini/run-1|ok|293|100|8.00|9.40|2ª tentativa, 293 s (≤600 s): ×0,7|**6.58**|


## Dois rankings oficiais (decisão do Lucas, 04/11/2026)

- **Ranking original**: vale para a configuração com limite de 180/300 s. É o deste relatório, com `resultados/notas_avaliador.csv`.
- **Ranking 7 min (420 s)**: as 70 run-1 que deram timeout em Claude, Codex e Gemini foram refeitas com 420 s. Fica em `resultados/_avaliador/cenario_7min/` (`RELATORIO_7MIN.md`, `notas_7min.csv`, `matriz_7min.csv`), em duas versões: **(i)** timeout = 0 e **(ii)** julgando a entrega parcial em `codigo/`.
- Nas 70 pastas refeitas, `avaliacao_avaliador.json` corresponde à execução original (180/300 s), cujos arquivos estão em `resultados/_timeouts_180s/` e `_timeouts_300s/`. Já `avaliacao_avaliador_7min.json` corresponde à execução de 420 s que está na pasta (`resultado.json`, `junit.xml`, `testes_saida.txt`, `codigo/`).
