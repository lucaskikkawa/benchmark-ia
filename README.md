# Benchmark IA

Projeto open-source e hobby que compara modelos de IA em tarefas práticas de programação em Python, considerando corretude, qualidade e tempo de execução. Não mede custo nem consumo de tokens.

## Estado atual

As **40 tarefas** foram criadas, o [piloto](resultados/piloto/PILOTO.md) foi realizado e a **Rodada 1 foi concluída e avaliada**. Houve refações de erros de cota e de timeouts; os detalhes e exceções estão nos [resultados da rodada](resultados/RODADA.md) e no [relatório do Avaliador](resultados/RELATORIO_AVALIADOR.md). O [site v2](site/index.html) permite explorar os resultados.

A Rodada 1 cobriu estes modelos, cada um com esforço `medium` e `high` (16 combinações):

- **Claude:** `claude-opus-5-5`, `claude-haiku-5-5`.
- **Codex:** `gpt-6.1-sol`, `gpt-6-luna`.
- **Gemini:** `gemini-4-argon`, `gemini-3.8-flash`.
- **Grok:** `grok-4.7`, `grok-4.7-build-fast`.

O site apresenta dois cenários: **Ranking A**, com os limites originais de 3 minutos em 31 tarefas e 5 minutos em 9; e **Ranking B**, no qual 70 execuções principais de Claude, Codex e Gemini que atingiram o limite foram refeitas com 7 minutos. O B não inclui Grok e apresenta tanto a regra de timeout igual a zero quanto uma alternativa que avalia a entrega parcial. Há uma regra excepcional para parte das execuções de `grok-4.7-high` no A; consulte os relatórios para os detalhes.

No Ranking A, `claude-haiku-5-5-high` ficou em primeiro, com nota 9,75. A tabela completa e suas ressalvas estão em [RODADA.md](resultados/RODADA.md); o [relatório de 7 minutos](resultados/_avaliador/cenario_7min/RELATORIO_7MIN.md) compara os cenários.

## Próximo passo: v3 planejada

A v3 está planejada e ainda não foi iniciada: avaliar `gemini-4-hydrogen` e `gemini-4-neon`, ambos em `medium` e `high`, com os mesmos critérios, reaproveitando os resultados de Claude e Codex. O site v3 não terá Grok na disputa; seus dados permanecem no repositório como legado, e Grok continua como autor de tarefas e juiz.

## Metodologia

São 10 tipos de tarefa, com uma versão criada por cada uma das quatro empresas. Cada combinação resolve as 30 tarefas das outras empresas, além de três repetições de uma tarefa para medir consistência. O ranking usa as 30 execuções principais, sem as repetições.

A nota de 0 a 10 combina **70% de testes e 30% de rubrica**: `0,7 × (% de testes / 10) + 0,3 × rubrica`. Na tarefa de escrever testes, a porcentagem mede mutantes eliminados. O Avaliador analisa código anonimizado com dois juízes de empresas diferentes da autora e da resolvedora; se um juiz falhar duas vezes, vale o outro. Em geral, timeout recebe zero, com as exceções e alternativas descritas acima. Veja a [metodologia e auditoria](resultados/RELATORIO_AVALIADOR.md) e o [plano original](PLANO.md).

## Como reproduzir

O plano previa Docker sem rede, mas o runner documentado usou `bwrap` para isolar o agente e `unshare -rn` para executar os testes ocultos sem rede; o agente precisa de acesso à API. O repositório não documenta comandos de Docker para essa execução. São necessários Python 3.12, `uv`, `bwrap`, `unshare` e as CLIs dos provedores configuradas. Veja [scripts/README-runner.md](scripts/README-runner.md).

```bash
uv venv -p 3.12 .bench-py
uv pip install -p .bench-py pytest mutmut pyyaml
.bench-py/bin/python scripts/run.py --empresa grok --modelo grok-4.7-build-fast --esforco medium --tarefa _exemplo
```

Para o piloto, a rodada e a avaliação, os scripts disponíveis são:

```bash
bash scripts/piloto.sh
.bench-py/bin/python scripts/rodada.py --dry-run
.bench-py/bin/python scripts/avaliador.py
```

A rodada retoma execuções existentes; a avaliação pode chamar juízes externos e gerar arquivos de resultados. Consulte os próprios scripts antes de executá-los.

## Organização

- [tarefas/](tarefas/): enunciados, metadados, rubricas, testes ocultos e soluções de referência; algumas tarefas incluem código inicial.
- [scripts/](scripts/): runner, piloto, rodada, avaliação e relatórios.
- [resultados/](resultados/): piloto, execuções, avaliações e relatórios.
- [site/](site/): site v2, construção e verificação.
- [notas/](notas/): registros de criação, revisão e validação das tarefas.
