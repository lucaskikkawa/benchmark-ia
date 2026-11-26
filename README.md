# Benchmark IA

Projeto open-source e hobby que compara modelos de IA em tarefas práticas de programação em Python, considerando corretude, qualidade e tempo de execução. Não mede custo nem consumo de tokens.

## Estado atual

As **40 tarefas** foram criadas, o [piloto](resultados/piloto/PILOTO.md) foi realizado e a **v3 foi julgada**. O [site 1.0](site/v3/index.html) apresenta os resultados; o [site v2](site/index.html) permanece disponível.

A v3 avaliou `gemini-4-hydrogen` e `gemini-4-neon` em `medium` e `high` e reaproveitou os resultados de Claude e Codex da Rodada 1. Grok está fora dos rankings, com seus dados mantidos no repositório como legado. Nesta versão, `grok-4.7-build-fast` ainda atua como juiz, e Grok também é autor de tarefas; por decisão de Lucas em 26/11/2026, não será usado como juiz nas próximas versões.

O **Ranking A**, de manchete, usa o prazo normal de 180 ou 300 segundos. O **Ranking B** refaz os timeouts com até 420 segundos, sem teto adicional para essas tentativas; 0,7 é o peso dos testes na nota. Há empate técnico quando a diferença entre notas é de até 0,30 ponto.

| Ranking A | Combinação | Nota |
| ---: | --- | ---: |
| 1 | `claude-haiku-5-5-high` | 9,75 |
| 2 | `claude-opus-5-5-medium` | 9,70 |
| 3 | `claude-haiku-5-5-medium` | 9,66 |
| 4 | `gemini-4-hydrogen-medium` | 9,53 |
| 5 | `claude-opus-5-5-high` | 9,39 |
| 6 | `gemini-4-hydrogen-high` | 9,29 |
| 7 | `gpt-6-luna-medium` | 9,09 |
| 8 | `gpt-6-luna-high` | 9,00 |
| 9 | `gemini-4-neon-medium` | 8,87 |
| 10 | `gpt-6.1-sol-medium` | 8,79 |
| 11 | `gemini-4-neon-high` | 8,18 |
| 12 | `gpt-6.1-sol-high` | 8,16 |

As médias no A são Claude **9,62**, Codex **8,76** e Gemini novo **8,97**; o Gemini antigo, presente apenas na Rodada 1, teve média **4,58**. Detalhes e Ranking B estão em [RODADA_V3.md](resultados/RODADA_V3.md); consulte também a [Rodada 1](resultados/RODADA.md) e o [relatório do Avaliador](resultados/RELATORIO_AVALIADOR.md).

## Metodologia

São 10 tipos de tarefa, com uma versão criada por cada uma das quatro empresas. Cada combinação resolve as 30 tarefas das outras empresas, além de três repetições de uma tarefa para medir consistência. O ranking usa as 30 execuções principais, sem as repetições.

A nota de 0 a 10 combina **70% de testes e 30% de rubrica**: `0,7 × (% de testes / 10) + 0,3 × rubrica`. Na tarefa de escrever testes, a porcentagem mede mutantes eliminados. O Avaliador analisa código anonimizado com dois juízes de empresas diferentes da autora e da resolvedora; se um juiz falhar duas vezes, vale o outro. Na v3, timeout recebe zero. Veja a [metodologia e auditoria](resultados/RELATORIO_AVALIADOR.md) e o [plano original](PLANO.md).

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
- [site/](site/): site v2, construção e verificação; [site/v3/](site/v3/) contém o site 1.0.
- [notas/](notas/): registros de criação, revisão e validação das tarefas.
