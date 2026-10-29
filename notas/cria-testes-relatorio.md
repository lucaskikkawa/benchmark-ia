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

---
# v2 — endurecimento (29/10/2026, horário de Brasília; branch tarefas-v2)

## Tempos
| Etapa | Duração |
|---|---|
| Worktree + padronização rubrica/meta por script (`scripts/padronizar.py`) | 17:49–17:50 |
| Endurecimento (4 em paralelo, 17:50) | Codex 6m47s · Gemini 17m08s · Claude 19m06s · Grok 22m27s → ~23 min |
| Revisão cruzada (4 em paralelo, 18:13) | Claude 3m14s · Codex 4m26s · Gemini 17m05s · Grok 41m05s → ~41 min |
| Validação, estimativa com Haiku, relatório, PR | ~10 min |
| **Total** | **~1h25 (17:49–19:10), com uma interrupção no meio (sem retrabalho)** |

## Padronização
- rubrica.yaml: `itens:` lista de 5 {id, criterio, 0, 1, 2} nas 40.
- meta.yaml: `timeout_min` (≤5) e `comando_teste` nas 40; novo campo `endurecimento`.

## Validação (scripts/validar.py → notas/validacao.json)
- 40/40 referência 100%. Testes por tarefa: 11 a 47 (antes ~8-20).
- 02/03: inicial/ falha em todas (03-refatoracao-gemini falha por erro de import da nova estrutura, válido).
- 08: 12-15 mutantes por tarefa, todos mortos pela suíte de referência.

## Estimativa de dificuldade (claude-haiku-5-5, medium, sem Docker)
01-funcao-codex 25/25, 04-dados-codex 47/47, 07-performance-grok 12/12, 09-api-gemini 46/46 → **100% nas 4**. A meta de 70-90% provavelmente NÃO foi atingida nessas; amostra pequena. Sugestão: medir no piloto v2 e, se continuar 100%, endurecer via enunciado (requisitos novos) em vez de só testes.

## Observações
- Revisões de Claude (sobre Codex) quase sem mudanças de novo; Gemini (sobre Grok) não atualizou o campo `revisao` em várias tarefas (texto da v1 ficou).
- Nenhuma CLI falhou por login/cota.

## Mudanças por tarefa (endurecimento | revisor: revisão)
| Tarefa | Endurecimento | Revisão |
|---|---|---|
| 01-funcao-claude | unidade w; dígitos só ASCII (rejeita ١/１/ſ/K); inteiros com milhares de dígitos exatos (limite int->str); tempo linear em ~1 MB de espaços (mata regex com backtracking); subclasse de str e bool | grok: sem mudanças |
| 01-funcao-codex | Recorte fechado opcional, validação integral, precisão arbitrária e oráculos determinísticos. | claude: sem mudanças |
| 01-funcao-gemini | Imutabilidade da lista de entrada, rejeição estrita de subclasses de int (como bool e tipos derivados), grandes volumes de dados desordenados e bordas com negativos e inteiros arbitrários. | codex: Oráculo completo no caso volumoso; mantidos tipos estritos e imutabilidade. |
| 01-funcao-grok | dígitos ASCII, validar antes de ignorar, fusão depois do recorte, list exata e 24:00 | gemini: sem mudanças |
| 02-bug-claude | docstring exige iterável qualquer (gerador/tupla), pares em lista, TypeError p/ não-int e bool, não mutar entrada; inicial ganhou sort in-place e validação que consome gerador; testes com 200k intervalos e oráculo aleatório | grok: 200k intervalos: comparação fora do assert (diff do pytest estourava o timeout) |
| 02-bug-codex | Janelas extensas, inteiros enormes, oráculo e independência entre chamadas. | claude: sem mudanças |
| 02-bug-gemini | Isolamento de estado interno (cópia profunda no construtor e em listar_itens), validação estrita de tipos com rejeição de bool e float em inteiros, validação de strings vazias e ordenação com unicode. | codex: Ordem Unicode sem locale explícita; erros de strings vazias conforme contrato. |
| 02-bug-grok | HALF_UP em 0.015/8.995/9.995, média arredondada só no fim, descarte da primeira mínima | gemini: sem mudanças |
| 03-refatoracao-claude | equivalência com o original embutido como oráculo: floats que mudam na 2ª casa (t*(1-taxa)), ordem/forma da soma do TOTAL, inf/nan, ordem das exceções em pedidos malformados, tipo exato; constantes TAXAS_DESCONTO/TAXAS_PADRAO/LIMITE_FAIXA_ALTA consultadas na chamada; 400 casos aleatórios | grok: enunciado explicita que pedidos e dicts aninhados não são alterados |
| 03-refatoracao-codex | Delegação ordenada com retornos distintos, geradores, categorias exatas e precisão inteira. | claude: sem mudanças |
| 03-refatoracao-gemini | Validações de domínio em ItemPedido, CalculadoraFrete e CalculadoraDesconto, verificação estrita de pré-arredondamento item-a-item vs soma global e suporte a pedidos com caracteres unicode e volume. | codex: Ordem e padrões da entrada explícitos; delegação e arredondamento de peso por item. |
| 03-refatoracao-grok | FAIXAS lida em cada chamada e expresso com // no total ímpar 2505 | gemini: sem mudanças |
| 04-dados-claude | BOM UTF-8, cabeçalho com espaços/CRLF, campos com aspas/vírgula/quebra de linha, nº de campos != cabeçalho é inválido, preço nan/inf inválido, conversão exatamente int()/float() (+3, 1e2), concluída com acento, desempate por str simples, tipos float/int no JSON, cria pais de saida, erro não cria/altera saida, arquivo vazio, 100k linhas | grok: sem mudanças |
| 04-dados-codex | BOM, CSV multilinha, números ASCII estritos, validação tardia e saída preservada. | claude: enunciado: explicita que minimo_centavos não-int (inclusive None, já testado) gera ValueError |
| 04-dados-gemini | Criação de diretórios de saída inexistentes, suporte a CSV de zero bytes, tolerância a espaços e BOM UTF-8, validação de tipo de top_n e dataset volumoso com 1000 linhas. | codex: Normalização de colunas e nomes e desempate explícitos; referência aceita cabeçalhos com espaços. |
| 04-dados-grok | CSV com aspas, CRLF e BOM, strip antes de agrupar, desempate lexicográfico e JSON exato | gemini: sem mudanças |
| 05-cli-claude | nova opção -x/--excluir repetível (com -i compara após lower); -i aplica str.lower() por palavra após extrair (İ, ß, ǅ; não casefold); sem normalização NFD; dígitos Unicode separam; stdin sempre UTF-8 estrito mesmo com terminal latin-1; arquivos grandes | grok: sucesso não exige stderr vazio (não está no enunciado) |
| 05-cli-codex | Flag top, Unicode difícil, volume, importação sem efeitos e main repetível. | claude: enunciado: explicita argv=None -> sys.argv[1:] (já testado); testes: timeout dos subprocessos 5/10s -> 20s (só anti-travamento) |
| 05-cli-gemini | Criação de subdiretórios pais para flag de saída, rejeição explícita de diretório como arquivo de entrada, arquivos com quebras de linha CRLF/LF mistas e pontuações aninhadas. | codex: Subprocessos da CLI com UTF-8 explícito, independentes do locale herdado. |
| 05-cli-grok | buracos de id, arquivo inválido preservado, strip Unicode e ano gregoriano | gemini: testes: subprocess com PYTHONIOENCODING=utf-8 e timeout=5 para evitar travamento e independência de locale |
| 06-multiarquivo-claude | novos requisitos: Livro valida campos (TypeError/ValueError), adicionar só Livro, busca com casefold e trecho vazio, validação do construtor, max_renovacoes + renovar() (ordem de erros, prazo nunca encurta, RenovacaoNegada), atrasados(), Emprestimo.renovacoes, __all__ exato, serviço enxerga o acervo vivo | grok: imports relativos via AST; busca ordena por comparação simples de str |
| 06-multiarquivo-codex | Validação JSON ampliada, integração em volume, saldos exatos e imutabilidade em falhas. | claude: sem mudanças |
| 06-multiarquivo-gemini | Propagação obrigatória de exceções quando dlq é None, eventos encadeados gerados dentro de handlers, despacho de tópicos sem inscritos e imutabilidade do histórico retornado. | codex: Ordem de publicação no histórico explicitada; demais exigências têm base no contrato. |
| 06-multiarquivo-grok | sem DV do ISBN, estoque por serviço, falha não altera estado, prazo atravessa o ano | gemini: sem mudanças |
| 07-performance-claude | novos parâmetros comprimento_min/comprimento_max (janela deslizante de prefixos, O(n)) com ValueError e casos min>max/min>n; inteiros > 64 bits; desempenho em subprocesso com 300k e janelas de milhares (mata O(n·L)); oráculo independente por busca binária | grok: comprimento_max=10**18 saiu do teste em processo (podia travar a suíte) |
| 07-performance-codex | Até um milhão de valores, distribuições adversas e memória O(k) medida em subprocesso. | claude: sem mudanças |
| 07-performance-gemini | Validação estrita de tipo int (rejeitando bool e floats), escala aumentada para 350.000 elementos e casos com inteiros gigantes. | codex: sem mudanças |
| 07-performance-grok | n=200000 no subprocesso, inteiros de 10**18 e produtos assimétricos de frequência | gemini: testes: medição de desempenho em subprocesso isolado com timeout de 8s para evitar travamento da suíte em soluções quadráticas |
| 08-testes-claude | 14 mutantes; trocados os 2 mais óbvios e acrescentados 3 sutis: dígito via isdigit (Unicode), classificar só com espaço/tab/quebra, ESPECIAIS sem _, última trinca ignorada, sem checagem de tipo (só morre com bytes/list) | grok: sem mudanças |
| 08-testes-codex | 14 mutantes: precisão, truncamento por linha, validação tardia e mutação após erro. | claude: sem mudanças |
| 08-testes-gemini | Inclusão de 12 mutantes sutis com bugs off-by-one em tamanhos e faixas de força, tabs/newlines em isspace, pontuação fora do conjunto permitido, repetições no final e parâmetros customizados do construtor. | codex: 12 mutantes não equivalentes; referência sem mensagens fixas e executor com UTF-8 explícito. |
| 08-testes-grok | mutantes sutis de subtração no NATAL, cupom em branco, 1900 e ano 1 | gemini: testes: adicionado PYTHONIOENCODING=utf-8 na execução dos mutantes |
| 09-api-claude | novos requisitos: orcamento_espera (desiste sem dormir; tentativas = requisições feitas), .status nos ErroAPI de HTTP, qualquer status não previsto sem retry (301/501), Retry-After sem diferenciar caixa e só finito >= 0, backoff sem OverflowError com milhares de tentativas, __cause__ None se última falha foi status, obter_varios aceita gerador e valida todos os ids antes | grok: sem mudanças |
| 09-api-codex | Subclasses, falhas transitórias no callback, backoff longo e chamadas independentes. | claude: sem mudanças |
| 09-api-gemini | Validação estrita de todos os parâmetros numéricos no construtor, preservação obrigatória de status_code no esgotamento de tentativas HTTP e rejeição imediata de status 3xx não-retentáveis. | codex: Cobertura dos tipos numéricos inválidos já exigidos no construtor. |
| 09-api-grok | sem cache de id, timeout interrompe a lista, slow com duas esperas e tuple rejeitado | gemini: testes: ampliada a margem de tempo em asserções de backoff e erro imediato para evitar falso negativo |
| 10-ambigua-claude | núcleo explícito ampliado: separadores repetidos/combinados, DDD sem dígito 0, fixo começa com 2-5, nunca completar/cortar dígitos; extração: ignora CPF/CNPJ/datas/CEP/valores, não recorta de sequência maior, separação por quebra de linha/;/,// e pontuação final, texto com 5000 telefones; casos ambíguos (0 inicial, 55 sem +, ramal, tipos) continuam fora dos testes | grok: sem mudanças |
| 10-ambigua-codex | Cópias rasas com aliases, extras, repetições em volume e empates sem política imposta. | claude: sem mudanças |
| 10-ambigua-gemini | Presença de SUPOSICOES.md sem mínimo de tamanho; imutabilidade do dicionário de entrada, preservação de identificadores com caracteres especiais/Unicode e suporte a grandes volumes de compras. | codex: Removidos tamanho mínimo da documentação e teste de campos extras; apenas núcleo explícito. |
| 10-ambigua-grok | núcleo Unicode sem normalizar: surrogate, lookalike, NBSP, texto longo e a palavra vazia | gemini: testes: asserção explícita de existência do arquivo SUPOSICOES.md |
