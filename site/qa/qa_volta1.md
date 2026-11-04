# QA do site — volta 1

**Veredito: passa**

> **Motor:** Gemini 3.8 Flash, esforço medium, via `agy` (log: `model alias "gemini-3.8-flash" resolved to "gemini-3.8-flash-medium"` e `label="Gemini 3.8 Flash (Medium)"` em `site/qa/agy_qa.log`; conversation_id 3d0bc8c0-ef3b-40dc-ac78-079085f69778).
> **Comando:** `agy -p "$(cat prompt_qa.txt)" --model gemini-3.8-flash --effort medium --dangerously-skip-permissions --add-dir /workspace/benchmark-ia --output-format json --log-file /workspace/benchmark-ia/site/qa/agy_qa.log` (em `site/qa/`; prompt em `prompt_qa.txt`).
> **Insumos:** `coletar.js` (Chrome headless, 390×844 e 1440×900; 5 abas × A, B nota_i e B nota_ii, além dos sliders a 0% e 100%) → `coleta.json` e `qa-*.png`; verdade recalculada das fontes em `verdade_A_run1.txt` (A, run-1, N=30) e `verdade.txt` (B).
> **Conferência do orquestrador:** console sem erros e nenhuma requisição fora de file:// nos dois viewports; `scrollWidth` = viewport em todos os estados; os 16 do A e os 12 do B (nota_i e nota_ii) batem com as fontes, assim como as médias por empresa e o high − medium. O argon no A mostra −0.26 (Δ das médias arredondadas 6.96 − 7.22; sem arredondar dá −0.2533). É o mesmo critério documentado no site para o caso do haiku (+0.09), então não conta como erro. O site e os prints `site-*.png` não foram alterados (sha256 conferido antes e depois).



### Contagem por gravidade
- **Bloqueante**: 0
- **Médio**: 0
- **Cosmético**: 0

---

### Tabela de erros

Nenhum erro bloqueante, médio ou cosmético foi encontrado. Todos os critérios especificados e recalculados foram atendidos com precisão.

| Gravidade | Onde (aba, viewport, elemento) | Esperado | Encontrado | Evidência |
|---|---|---|---|---|
| — | — | — | — | Nenhuma divergência detectada |

---

### Conferido e OK

1. **5 abas navegáveis**:
   - `Ranking`, `Comparar`, `Esforço`, `Tarefas` e `Avaliador` presentes no `#nav`, ativas e alternando estados perfeitamente em mobile (390×844) e desktop (1440×900).
2. **Seletor A/B e explicações**:
   - Seletor `#cenA` (🅰️ Ranking A, 3/5 min, 16 combinações) e `#cenB` (🅱️ Ranking B, 7 min, 12 combinações, sem Grok) visível no topo com o texto explicativo correto (`#cenTxt`).
3. **Toggle `nota_i` / `nota_ii` exclusivo do Ranking B**:
   - Elemento `#nvSeg` fica oculto no Ranking A (`nvSegVisivel: false`) e visível apenas quando o Ranking B é selecionado (`nvSegVisivel: true`). Alterna dinamicamente entre `nota_i (timeout = 0)` e `nota_ii (entrega parcial julgada)`.
4. **Sliders e filtros**:
   - Controle de peso (0% a 100% testes/rubrica) recalcula o ranking ao vivo com animação. Testado nos extremos `0%` e `100%` e resetado com sucesso pelo `#btReset`.
5. **Números do ranking (2 casas decimais) e médias contra a verdade**:
   - **Ranking A**: todas as 16 combinações batem com [verdade_A_run1.txt](file:///workspace/benchmark-ia/site/qa/verdade_A_run1.txt) e [RELATORIO_AVALIADOR.md](file:///workspace/benchmark-ia/resultados/RELATORIO_AVALIADOR.md) (N=30) dentro da tolerância de 0,005 (ex.: `claude-haiku-5-5-high` 9.75, `claude-opus-5-5-medium` 9.70, ..., `gemini-3.8-flash-high` 1.31).
   - **Ranking B (`nota_i` e `nota_ii`)**: todas as 12 combinações batem com [resumo_7min.json](file:///workspace/benchmark-ia/resultados/_avaliador/cenario_7min/resumo_7min.json) e [verdade.txt](file:///workspace/benchmark-ia/site/qa/verdade.txt) (ex.: na `nota_ii`, `gemini-4-argon-high` sobe para 9.18 em 8º lugar; na `nota_i`, fica em 10º com 8.52).
   - **Médias por empresa**:
     - *Ranking A*: Claude 9.62, Codex 8.76, Grok 5.52, Gemini 4.58 (conferência exata com o relatório).
     - *Ranking B (`nota_i`)*: Claude 9.71, Codex 9.30, Gemini 7.63.
     - *Ranking B (`nota_ii`)*: Claude 9.71, Codex 9.30, Gemini 8.54.
   - **High − Medium (lado a lado)**:
     - Gráfico e tabela lado a lado exibem os deltas para A, B i e B ii corretamente (Haiku +0.09/+0.10, Opus −0.31/+0.01/+0.01, Luna −0.09/+0.19/+0.19, Sol −0.63/−0.02/−0.02, Argon −0.26/−0.57/+0.08, Flash −1.54/−2.80/−1.71, Groks com "sem Grok no B"). Conclusão textual conforme plano V2.2.
6. **Marcação da `10-ambigua-claude`**:
   - Exibição de 0% mantido na nota, com o badge `"⏱ timeout sem entrega (Gemini e Grok); tarefa validada"`.
   - Detalhamento explícito dos 4 modelos Codex resolvendo com 40 a 42 de 42 testes (`gpt-6-luna high` 40/42, `gpt-6-luna medium` 40/42, `gpt-6.1-sol high` 42/42, `gpt-6.1-sol medium` 42/42), e citação ao arquivo de análise `_avaliador/analise_10_ambigua_claude.md`.
7. **Selo ⚖️ isolado no Ranking A**:
   - Selo `⚖️ ×0,7/×0,5` exibido unicamente no `grok-4.7-high` no Ranking A. Nenhuma ocorrência indevida no Ranking B ou em abas secundárias.
8. **Textos, ortografia e idioma**:
   - Português impecável em títulos, legendas, cards explicativos, rodapés e notas metodológicas. Acentuação e pontuação corretas; termos técnicos em inglês preservados apenas onde apropriado (`high`, `medium`, `run-1`, `timeout`, nomes de modelos).
9. **Layout mobile (390×844) e integridade visual**:
   - `scrollWidth` estritamente igual a 390 px em todos os estados de tela coletados (sem quebra ou rolagem horizontal da página).
   - As tabelas reportadas no extrator de overflow estão corretamente aninhadas dentro de contêineres `.tw` com `overflow-x: auto` sob tags `<details class="vt">`, garantindo visualização sem cortes ou quebra de fluxo.
   - Zero erros no console do navegador, zero exceções de página e nenhuma chamada a recursos externos (100% autocontido).
