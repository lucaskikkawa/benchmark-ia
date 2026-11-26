# QA final do site 1.0 (v3) — Gemini

- **Data/hora:** 26/11/2026, 18:18 (America/Sao_Paulo)
- **Motor:** Gemini 4 Neon (Medium) (`gemini-4-neon-medium`) via `agy`
- **Alvo:** `site/v3/index.html` (gerado com `site/v3/dados-v3.json`, commit `d7f4577`, 2 juízes nas avaliações v3)
- **Veredito:** **passa** (nenhum bloqueador encontrado; 1 omissão textual não bloqueadora registrada abaixo).

## Verificação automatizada (`verificar_v3.js`)

- Log oficial em `site/v3/qa/verificacao-final.log` (26/11/2026, 18:15): **224 verificações aprovadas**, zero falhas, zero erros/avisos de console, `pageerror` ou requisições externas, encerrado com **`TUDO OK`** (`EXIT:0`) em desktop (1280 px) e celular (390 px).
- Conferência direta do HTML (`<script id="dados">` e `<script id="dados-v3">`): `status: "ok"`, 120 entradas em `runsA` e 120 em `runsB`, 0 tarefas `*-gemini` e 0 execuções `ok` com menos de 2 juízes.

## Itens conferidos

1. **Abertura em v3 + prazo normal (Ranking A):** confirmado em `site/v3/qa/desktop-abertura.png` e `site/v3/qa/celular-abertura.png`. Seletores "Teste novo (v3 · Gemini novos)" e "Prazo normal (3 a 5 min)" ativos; não abre em B.
2. **Sem "aguardando rodada v3" nem faixa de mock:** confirmado nas capturas de abertura e rankings v3 (`desktop-abertura.png`, `desktop-ranking-v3-estendido.png`, `celular-abertura.png`).
3. **Ranking v3 A (12 versões, sem Grok):** notas e ordem idênticas ao `resultados/RODADA_V3.md` — 1º Haiku high **9,75**, 2º Opus medium **9,70**, 3º Haiku medium **9,66**, 4º Hydrogen medium **9,53**, 5º Opus high **9,39**, 6º Hydrogen high **9,29**, 7º Luna medium **9,09**, 8º Luna high **9,00**, 9º Neon medium **8,87**, 10º Sol medium **8,79**, 11º Neon high **8,18**, 12º Sol high **8,16**.
4. **Ranking v3 B (12 versões, sem Grok):** notas idênticas ao `RODADA_V3.md` — Haiku high **9,75** (1º) até Neon high **8,84** (12º), com Neon medium **9,20** (10º) e empate em **9,29** entre Luna high (8º) e Hydrogen high (9º), marcado como empate técnico (`desktop-ranking-v3-estendido.png`, `celular-ranking-v3-estendido.png`).
5. **Médias por empresa (v3):**
   - Prazo A: Claude **9,62** · Gemini novo **8,97** · Codex **8,76** (bate com `RODADA_V3.md`).
   - Prazo B: Claude **9,71** · Codex **9,29** · Gemini novo **9,21** (bate com `RODADA_V3.md`).
6. **Card "Gemini antigo × Gemini novo":** preenchido nos dois prazos — no A, melhor antigo Argon medium **7,22** vs. Hydrogen medium **9,53** (+2,32 ponto); no B, Argon medium **9,09** vs. Hydrogen medium **9,53** (+0,44 ponto). Flash e Argon aparecem apenas nesse card e na visão Rodada 1.
7. **Grok fora da disputa e aba "Por que o Grok saiu":** Grok ausente dos rankings, gráficos e comparações. A aba explica que ele continua como autor de tarefas e juiz nesta versão (`desktop-mais-grok.png`, `celular-mais-grok.png`), mas **omite** a decisão de que ele não será juiz nas próximas versões (ver seção abaixo).
8. **Rodada 1 intacta:** médias por empresa no A = Claude **9,62** · Codex **8,76** · Gemini **4,58** (`desktop-ranking-r1-normal.png`); no B = Claude **9,71** · Codex **9,29** · Gemini **7,63** (`desktop-ranking-r1-estendido.png`).
9. **Linguagem e aba Técnico:** abas principais (`Ranking`, `Comparar`, `Esforço`, `Tarefas`, `Por que confiar`) sem jargão técnico; aba `Técnico` (`desktop-mais-tecnico.png`) organizada com índice de 9 seções e selo verde de conferência.
10. **Layout desktop (1280 px) e celular (390 px):** sem rolagem horizontal evidente ou quebra visual nas capturas inspecionadas (`desktop-*.png` e `celular-*.png`) e validado pelo `verificar_v3.js`.

## Erros / pendências

- **Bloqueadores:** nenhum (sem número errado, abertura correta em v3/A, sem Grok no ranking, sem placeholder/mock, sem quebra visual).
- **Omissão textual (não bloqueadora) — aba "Por que o Grok saiu":** o texto em `#sub-grok` (`site/v3/qa/desktop-mais-grok.png` e `site/v3/qa/celular-mais-grok.png`) informa que o Grok continua como autor e juiz, mas **não menciona que ele deixará de ser juiz nas próximas versões** (decisão de 26/11/2026 em `resultados/RODADA_V3.md`, linha 9).
  - Recorte atual em `site/v3/index.html` (`#sub-grok`): `"Como juiz. O Grok build-fast é um dos 4 juízes do Avaliador. Ele julga às cegas e nunca julga a própria empresa. Sem ele, faltaria o segundo juiz em boa parte das soluções."` (0 ocorrências no HTML para `"próxima"` / `"deixará"` / `"não será juiz"`).
  - Recomendação opcional: acrescentar uma frase ao parágrafo "Como juiz" indicando que ele ainda julga esta versão e não será juiz nas próximas.
