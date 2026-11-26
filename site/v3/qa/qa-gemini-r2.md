# QA do site v3 — Gemini / Codex, rodada 2

- **Data/hora:** 25/11/2026, 18:55 (America/Sao_Paulo)
- **Motor:** CLI Codex · `gpt-6-luna` · esforço `medium`
- **Comando:** `codex exec -m gpt-6-luna -c model_reasoning_effort="medium" -C /workspace/benchmark-ia -s workspace-write --skip-git-repo-check -o /workspace/benchmark-ia/.motor/bench-gemini-qa-v3-r2/saida.txt "Leia /workspace/benchmark-ia/.motor/bench-gemini-qa-v3-r2/PEDIDO.md e faça o que pede"`
- **Veredito: passa.** Os dois itens da r1 foram resolvidos; não encontrei erro novo comprovado.

## Itens da r1

1. **Abertura em B — resolvido.** O estado inicial agora é teste v3 com prazo normal (A): `abertura.json` registra `teste: v3`, `prazo: A`, `prazoA: true` e `prazoB: false`. A captura [desktop, abertura](/workspace/benchmark-ia/site/v3/qa/qa-r2-desktop-abertura.png) confirma os seletores “Teste novo” e “Prazo normal” ativos; a captura [celular, abertura](/workspace/benchmark-ia/site/v3/qa/qa-r2-celular-abertura.png) e o log confirmam o mesmo estado em 390 px. O item 8 de `decisoes-v3.md` é atendido.
2. **Média Gemini 4,58 vs. 4,59 / método — resolvido.** O valor exibido é 4,58 e corresponde à média das quatro notas de versão já arredondadas a duas casas, conforme `RODADA.md`. A aba Técnico explica explicitamente o método e a diferença de 0,01 frente à média direta dos 120 resultados (`app.html`, parágrafo de médias por empresa). A tela [Rodada 1, prazo normal](/workspace/benchmark-ia/site/v3/qa/qa-r2-desktop-ranking-r1-normal.png) mostra Gemini 4,58. Não há erro nesse número.

## Erros novos

Nenhum erro novo comprovado nas abas, nos tamanhos examinados, nos textos ou nos números. Não há contagem de erros novos.

## Verificação automatizada e headless

**Passou:** o log de `verificar_v3.js` registra 222 verificações aprovadas, nenhuma falha e termina com “TUDO OK”. A execução do Chrome/verificador foi feita na box, fora da sandbox do Codex, como na r1. O log cobre desktop 1280 px e celular 390 px, navegação, rankings A/B de Rodada 1 e v3, Comparar, Esforço, Tarefas, Mais, modo mock e estados de interação. Não houve rolagem horizontal nas verificações; o estado inicial abriu em v3/A; o bloco v3 “aguardando rodada v3” aparece conforme esperado. O log também confirma zero erros/avisos de console, `pageerror` ou requisições externas.

As capturas de abertura mostram título “Benchmark 1.0 — IAs que programam”, sem overflow horizontal nos dois viewports. Inspecionei também as telas de ranking normal e estendido: a média Gemini da Rodada 1 é 4,58 no prazo normal, e no prazo estendido as médias exibidas são Claude 9,71, Codex 9,29 e Gemini 7,63. As telas de abertura/rankings v3 preservam o aviso de dados pendentes para Hydrogen e Neon, como previsto.

## Números recalculados

Usei `recalc_medias.txt` e conferi o método descrito em `resultados/RODADA.md`, os dados de `resumo_7min.json` e a explicação em `site/v3/LEIA-ME.md`/aba Técnico. O método é: arredondar cada média de versão para duas casas e depois calcular a média simples entre versões da empresa.

- **Rodada 1, prazo normal (A), sem Grok:** Claude = **9,62**; Codex = **8,76**; Gemini = **4,58**. Valores exibidos conferem com a fonte e com a captura [desktop](/workspace/benchmark-ia/site/v3/qa/qa-r2-desktop-ranking-r1-normal.png).
- **Rodada 1, prazo estendido (B), sem Grok:** Claude = **9,71**; Codex = **9,29**; Gemini = **7,63**. Captura [desktop](/workspace/benchmark-ia/site/v3/qa/qa-r2-desktop-ranking-r1-estendido.png) confere com as fontes.
- **Codex no prazo de 7 min:** versões arredondadas `[9,29; 9,09; 9,39; 9,41]`; média = 9,295, exibida **9,29** segundo o método oficial do site. A média das notas não arredondadas seria 9,30; a aba Técnico explica a diferença. Isso não é erro.
- **Contexto v3:** Hydrogen e Neon seguem pendentes. Claude e Codex aparecem com os resultados reaproveitados: no A, médias 9,62 e 8,76; no B, 9,71 e 9,29. A média Gemini do v3 não é calculável enquanto as quatro versões novas aguardam resultados.
