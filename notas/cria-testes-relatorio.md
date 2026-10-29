# Relatório — Cria Testes (29/10/2026, horário de Brasília)

## Tempos
| Etapa | Duração |
|---|---|
| Geração (4 em paralelo, início 15:02) | Codex 10m23s · Claude 13m27s · Gemini 13m55s · Grok 26m54s → parede ≈27 min |
| Revisão cruzada (4 em paralelo, início 15:37) | Claude 2m05s · Codex 9m01s · Gemini 16m39s · Grok 19m48s → parede ≈20 min |
| Validação, seleção, git/PR | ≈10 min |
| **Total** | **≈1h10 (15:00–16:10), incluindo a interrupção** |

## Comandos
- Codex: `codex exec -m gpt-6.1-sol -c model_reasoning_effort=high`
- Claude: `claude -p --model claude-opus-5-5 --effort high`
- Gemini: `agy -p --model gemini-3.8-flash-high`
- Grok: `grok -p -m grok-4.7 --effort high`
Prompts em `notas/prompt-geracao.md` e `notas/prompt-revisao.md`; logs em `notas/logs/`.

## Revisão (autor → revisor)
gemini→codex, codex→claude, claude→grok, grok→gemini. Campo `revisor` e `revisao` em cada meta.yaml. ~20 de 40 tarefas tiveram testes ajustados (bordas extras, remoção de exigências não especificadas, subprocess com PYTHONIOENCODING e timeout, medição de performance em subprocesso).

## Validação (`scripts/validar.py`, resultado em `notas/validacao.json`)
- 40/40: referência passa 100% nos testes ocultos.
- 02/03 (8 tarefas): `inicial/` falha nos testes relevantes.
- 08 (4 tarefas): 10 mutantes (Claude 11); a suíte de referência mata todos e passa no módulo correto.
- Validação feita com Python local (sem Docker no box); rodar no container no piloto.

## Problemas / observações
- Nenhuma CLI falhou por login/cota.
- A revisão do Claude (sobre Codex) foi rápida (2 min) e não mudou nada; menos rigorosa que as outras.
- O repositório é compartilhado com outro agente (branch `ambiente`), que trocou a branch do diretório durante o trabalho e commitou versões pré-revisão de `01-funcao-gemini` e `02-bug-gemini` e `tarefas/_exemplo` em `ambiente`. As versões revisadas estão na branch `tarefas`; ao mesclar as duas, prefira as de `tarefas`.
- Piloto/consistência: ver `tarefas/SELECAO.md`.
