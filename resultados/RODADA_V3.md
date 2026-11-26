# Rodada v3 — resultados do Avaliador

26/11/2026 · America/Sao_Paulo

Cada combinação tem **30 tentativas principais**. As repetições de consistência ficam fora do ranking. Claude e Codex reutilizam as notas publicadas na Rodada 1. Hydrogen e Neon foram avaliados nesta rodada com o mesmo protocolo de dois juízes neutros por solução, de empresas distintas da resolvedora e da autora da tarefa. O código é anonimizado. [Metodologia da Rodada 1](RELATORIO_AVALIADOR.md)

**Nota (0–10)** = `0,7 × (%testes / 10) + 0,3 × rubrica`. A rubrica é a média das notas válidas dos juízes. Timeout vale zero. O **Ranking A**, manchete da rodada, usa o prazo original de 180 s ou 300 s, conforme a tarefa. O **Ranking B** usa a nota `ni` e substitui os timeouts do prazo original por novas tentativas de até 420 s. O peso dos testes é 70% da nota, sem teto adicional nas novas tentativas. [Cenário de 7 minutos da Rodada 1](_avaliador/cenario_7min/RELATORIO_7MIN.md).

**Decisão do Lucas (26/11/2026).** O Grok (`grok-4.7-build-fast`) ainda julga esta versão e deixará de ser usado nas próximas.

## Ranking A — prazo normal

| Posição | Combinação | Nota |
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

## Ranking B — prazo estendido (420 s, `ni`)

| Posição | Combinação | Nota |
| ---: | --- | ---: |
| 1 | `claude-haiku-5-5-high` | 9,75 |
| 2 | `claude-opus-5-5-high` | 9,71 |
| 3 | `claude-opus-5-5-medium` | 9,70 |
| 4 | `claude-haiku-5-5-medium` | 9,66 |
| 5 | `gemini-4-hydrogen-medium` | 9,53 |
| 6 | `gpt-6.1-sol-medium` | 9,41 |
| 7 | `gpt-6.1-sol-high` | 9,39 |
| 8 | `gemini-4-hydrogen-high` | 9,29 |
| 8 | `gpt-6-luna-high` | 9,29 |
| 10 | `gemini-4-neon-medium` | 9,20 |
| 11 | `gpt-6-luna-medium` | 9,09 |
| 12 | `gemini-4-neon-high` | 8,84 |

### Empates técnicos

Há empate técnico quando as notas publicadas de duas combinações diferem em **até 0,30 ponto**. Cada intervalo abaixo reúne posições cujas notas atendem ao limite par a par. Um intervalo pode compartilhar posições com outro, e o critério vale separadamente em cada um.

| Ranking | Grupos de posições em empate técnico |
| --- | --- |
| A | 1–4, 3–5, 4–6, 5–7, 6–8, 7–10 e 11–12 |
| B | 1–5, 2–6, 4–7, 5–8, 6–10, 7–11 e 11–12 |

No B, Hydrogen high e Luna high dividem a 8ª posição com **9,29**.

## Timeouts do Gemini novo

| Combinação | A | B |
| --- | ---: | ---: |
| `gemini-4-hydrogen-medium` | 0 | 0 |
| `gemini-4-hydrogen-high` | 1 | 1 |
| `gemini-4-neon-medium` | 2 | 1 |
| `gemini-4-neon-high` | 4 | 2 |
| **Total** | **7** | **4** |

O timeout de Hydrogen medium refeito com 420 s ocorreu numa repetição de consistência, fora do N do ranking.

## Gemini antigo × novo — Ranking A

| Gemini antigo | Nota | Gemini novo | Nota |
| --- | ---: | --- | ---: |
| `gemini-3.8-flash-medium` | 2,85 | `gemini-4-hydrogen-medium` | 9,53 |
| `gemini-3.8-flash-high` | 1,31 | `gemini-4-hydrogen-high` | 9,29 |
| `gemini-4-argon-medium` | 7,22 | `gemini-4-neon-medium` | 8,87 |
| `gemini-4-argon-high` | 6,96 | `gemini-4-neon-high` | 8,18 |
| **Média** | **4,58** | **Média** | **8,97** |

## Médias por empresa

| Empresa | A | B (`ni`) |
| --- | ---: | ---: |
| Claude | 9,62 | 9,71 |
| Codex | 8,76 | 9,29 |
| Gemini novo | 8,97 | 9,21 |

O método da Rodada 1 e do site arredonda cada versão a duas casas, calcula a média simples das quatro versões e arredonda o resultado a duas casas. No B, a média do Codex é 9,295 em decimal e aparece como **9,29** com o arredondamento em ponto flutuante do site. O relatório de 7 minutos publica 9,30 a partir das médias de versão sem arredondamento prévio. [Rodada 1](RODADA.md) · [Método do site](../site/v3/LEIA-ME.md)

## Auditoria e viés

- **0 incoerências** e **0 erros** na reexecução dos testes ocultos.
- Após Lucas reativar a assinatura do Claude, o refill completou **33 de 33** julgamentos do Neon entre 17:53 e 17:59 de 26/11/2026. As **128 avaliações v3** de Hydrogen e Neon, incluindo as repetições de consistência, agora têm **dois juízes válidos**. A auditoria registrou **0 avaliações com um só juiz** (`single_judge_count=0`).

As estatísticas por juiz consideram as 116 avaliações da consolidação dos rankings, incluindo as novas tentativas de 420 s com nota.

| Juiz | Média de rubrica |
| --- | ---: |
| Codex | 8,368 |
| Grok | 8,566 |
| Claude | 8,400 |

| Juízes | Avaliações em comum | Diferença absoluta média |
| --- | ---: | ---: |
| Codex × Grok | 36 | 0,972 |
| Claude × Grok | 40 | 0,200 |
| Claude × Codex | 40 | 1,150 |

## Dados

- Dados do site em [`site/v3/dados-v3.json`](../site/v3/dados-v3.json).
- Notas e auditoria em [`resultados/_avaliador/v3/`](_avaliador/v3/), com o [CSV de notas](_avaliador/v3/notas_v3.csv) e o [resumo da fase 2](_avaliador/v3/resumo_v3.json). As notas de Claude e Codex vêm dos CSVs da Rodada 1 para o [prazo normal](_avaliador/notas_avaliador.csv) e o [prazo estendido](_avaliador/cenario_7min/notas_7min.csv).
