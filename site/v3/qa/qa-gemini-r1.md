# QA do site v3 — Gemini / Codex, rodada 1

- **Data/hora:** 25/11/2026, 18:41 (America/Sao_Paulo)
- **Motor:** CLI Codex · `gpt-6-luna` · esforço `medium`
- **Comando:** `codex exec -m gpt-6-luna -c model_reasoning_effort="medium" -C /workspace/benchmark-ia -s workspace-write --skip-git-repo-check -o /workspace/benchmark-ia/.motor/bench-gemini-qa-v3-r1/saida.txt "Leia /workspace/benchmark-ia/.motor/bench-gemini-qa-v3-r1/PEDIDO.md e faça o que pede"`
- **Veredito: não passa.** Há 1 item bloqueante, o prazo inicial está em B apesar da decisão vigente exigir A.

## Verificação automatizada e headless

A reexecução foi feita na box, fora da sandbox do Codex, porque o Chrome falhou dentro da sandbox com erro do Crashpad. O script usado foi a cópia `verificar_v3_r1.js`, que mudou somente os caminhos dos prints para usar o prefixo `qa-r1-`; `site/v3/verificar_v3.js` original permaneceu intacto. O resultado foi **216 aprovações, 0 falhas e “TUDO OK”**. O log integral está em [verificar_v3_box.log](/workspace/benchmark-ia/.motor/bench-gemini-qa-v3-r1/verificar_v3_box.log).

A verificação cobriu desktop 1280 px e celular 390×844, navegação e seletores, rankings A/B, comparação, esforço, mapa de tarefas, área Mais, estado pendente do v3, modo mock, movimento reduzido e links com hash. Nas abas verificadas não houve rolagem horizontal, erros ou avisos de console, erros de página ou requisições externas. O script original ainda testa e confirma “abre no prazo estendido (manchete B)”, expectativa antiga que conflita com o item 8 das decisões.

Na abertura capturada, ambos os viewports mostram v3 e prazo B, com `overflowX=false`, console sem erros e rede sem requisições. As evidências são [desktop, abertura](/workspace/benchmark-ia/site/v3/qa/qa-r1-desktop-abertura.png) e [celular, abertura](/workspace/benchmark-ia/site/v3/qa/qa-r1-celular-abertura.png). Foram gravados 44 prints novos com prefixo `qa-r1-`, sem sobrescrever os anteriores. Também conferi as telas do ranking normal em [desktop](/workspace/benchmark-ia/site/v3/qa/qa-r1-desktop-ranking-r1-normal.png) e [celular](/workspace/benchmark-ia/site/v3/qa/qa-r1-celular-ranking-r1-normal.png).

## Erros e desvios

1. **Gravidade: bloqueante.** **Onde:** estado inicial do prazo, em `site/v3/app.html` e `site/v3/index.html`. **Fato:** o site abre em v3 com prazo B/estendido. O item 8 de `site/planejamento/decisoes-v3.md` determina abertura em v3 com prazo normal/Ranking A. A captura inicial e o log confirmam B. O script original também espera B, alinhado à implementação antiga. **Correção sugerida:** mudar a manchete inicial para A e atualizar a asserção do verificador e a documentação que ainda indiquem B como padrão.
2. **Gravidade: cosmético, diferença de agregação.** **Onde:** média por empresa Gemini na Rodada 1. **Fato:** a fonte `resultados/RODADA.md` e o site mostram 4,58. A média direta dos 120 valores individuais, sem arredondar antes as médias das quatro versões, resulta em 4,59. A métrica publicada usa média das versões arredondadas e resulta em 4,58; portanto, o valor mostrado pelo site bate com a fonte oficial. **Correção sugerida:** deixar explícito na explicação técnica que a média por empresa usa as médias das versões arredondadas.

## Números recalculados

Recalculei as médias a partir das tentativas principais embutidas no HTML, agrupadas por versão. Para A, comparei os resultados com `resultados/RODADA.md`. Para B, usei `nota_i` e conferi com `resultados/_avaliador/cenario_7min/resumo_7min.json`.

- **Rodada 1, prazo normal (A), ranking sem Grok:** Haiku high 9,75; Opus medium 9,70; Haiku medium 9,66; Opus high 9,39; Luna medium 9,09; Luna high 9,00; Sol medium 8,79; Sol high 8,16; Argon medium 7,22; Argon high 6,96; Flash medium 2,85; Flash high 1,31. Posições e notas arredondadas conferem com a fonte.
- **High − medium, prazo normal (A):** Haiku +0,09; Opus −0,31; Flash −1,54; Argon −0,26; Luna −0,09; Sol −0,63. Conferem com a tabela da Rodada 1.
- **Médias por empresa, prazo normal (A):** Claude 9,62; Codex 8,76; Gemini 4,58. Conferem com `RODADA.md` e com a tela [do ranking normal](/workspace/benchmark-ia/site/v3/qa/qa-r1-desktop-ranking-r1-normal.png).
- **Prazo estendido (B), ranking sem Grok:** Haiku high 9,75; Opus high 9,71; Opus medium 9,70; Haiku medium 9,66; Sol medium 9,41; Sol high 9,39; Luna high 9,29; Luna medium 9,09; Argon medium 9,09; Argon high 8,52; Flash medium 7,85; Flash high 5,05. Os números correspondem às médias do resumo 7 min formatadas com o arredondamento do site; Sol medium tem média subjacente 9,415 e aparece como 9,41.
- **High − medium, prazo estendido (B):** Haiku +0,10; Opus +0,01; Flash −2,80; Argon −0,57; Luna +0,19; Sol −0,02. Sol tem diferença subjacente −0,025, formatada como −0,02 pelo arredondamento do site.

## Conformidade e linguagem

As capturas e o verificador cobrem as abas principais e a área Mais. O log confirma os controles e os estados previstos, sem overflow horizontal nos dois tamanhos, erros ou avisos de console, nem tráfego externo. O bloco “aguardando rodada v3” aparece como esperado. Não encontrei outro desvio comprovado além do prazo inicial e da nota de arredondamento já descrita.
