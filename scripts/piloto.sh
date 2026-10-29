#!/bin/bash
# Piloto: 4 empresas em paralelo, sequencial dentro de cada uma (Gemini: Flash antes do Argon).
cd "$(dirname "$0")/.."
P=.bench-py/bin/python
emp() { e=$1; t=$2; shift 2; for m in "$@"; do for x in medium high; do
  echo "$(date +%T) START $e $m $x"; $P runner/run.py --empresa $e --modelo $m --esforco $x --tarefa $t > /tmp/piloto-$e-$m-$x.json 2>&1
  echo "$(date +%T) END $e $m $x $(grep -o '"status": "[a-z]*"' /tmp/piloto-$e-$m-$x.json)"; done; done; }
emp codex 01-funcao-claude gpt-6-luna gpt-6.1-sol &
emp claude 01-funcao-codex claude-haiku-5-5 claude-opus-5-5 &
emp gemini 01-funcao-codex gemini-3.8-flash gemini-4-argon &
emp grok 01-funcao-codex grok-4.7-build-fast grok-4.7 &
wait
