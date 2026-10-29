# Runner

Exemplo: `.bench-py/bin/python runner/run.py --empresa grok --modelo grok-4.7-build-fast --esforco medium --tarefa _exemplo`

Ambiente: venv Python 3.12 (`uv venv -p 3.12 .bench-py && uv pip install -p .bench-py pytest mutmut pyyaml`).
Os testes ocultos rodam sem rede via `unshare -rn`. Docker não está disponível no box por enquanto (alternativa ao PLANO).
O agente CLI roda no host, numa pasta temporária limpa que não tem os testes ocultos.
