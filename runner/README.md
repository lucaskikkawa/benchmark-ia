# Runner

Exemplo: `.bench-py/bin/python runner/run.py --empresa grok --modelo grok-4.7-build-fast --esforco medium --tarefa _exemplo`

Ambiente: venv Python 3.12 (`uv venv -p 3.12 .bench-py && uv pip install -p .bench-py pytest mutmut pyyaml`).
Os testes ocultos rodam sem rede via `unshare -rn`. Docker não está disponível no box por enquanto (alternativa ao PLANO).
O agente CLI roda no host, numa pasta temporária limpa que não tem os testes ocultos.

## Isolamento (bwrap)
O agente roda em `bwrap`. Ele vê só a pasta da execução (rw), os binários do sistema (ro) e as configs das CLIs (~/.codex, ~/.claude*, ~/.grok, ~/.gemini, rw). `/workspace` (tarefas, testes ocultos, resultados) fica invisível. A rede continua liberada pra API.

## Mapa de IDs (--modelo + --esforco)
| Empresa | Modelo (--modelo) | Esforço |
|---|---|---|
| codex | gpt-6.1-sol, gpt-6-luna | `-c model_reasoning_effort=medium/high` |
| claude | claude-opus-5-5, claude-haiku-5-5 | `--effort medium/high` |
| gemini | gemini-3.8-flash, gemini-4-argon | o runner monta o ID `<modelo>-<esforço>` (ex.: gemini-3.8-flash-medium) |
| grok | grok-4.7, grok-4.7-build-fast | `--effort medium/high` |
