# Análise — tarefa 10-ambigua-claude (sem mudar notas, sem commit)

## 1. Desempenho por modelo (run-1)
A tarefa é da autoria da Claude, então a Claude não a resolve.

|Modelo|Status oficial|Testes|Duração (s)|Nota oficial|Cenário 7 min|
|-|-|-|-|-|-|
|gpt-6-luna-high|ok|40/42|59|8,62|—|
|gpt-6-luna-medium|ok|40/42|30|9,22|—|
|gpt-6.1-sol-high|ok|42/42|169|9,70|—|
|gpt-6.1-sol-medium|ok|42/42|101|9,40|—|
|gemini-3.8-flash-high|timeout (180 s)|0/1 (coleta)|180|0|timeout 420 s, 0%, 0|
|gemini-3.8-flash-medium|timeout (180 s)|0/1|180|0|timeout 420 s, 0%, 0|
|gemini-4-argon-high|timeout (180 s)|0/1|180|0|timeout 420 s, 0%, 0|
|gemini-4-argon-medium|timeout (180 s)|0/1|180|0|timeout 420 s, 0%, 0|
|grok-4.7-build-fast-high|timeout|0/1|186|0|—|
|grok-4.7-build-fast-medium|timeout|0/1|180|0|—|
|grok-4.7-high|timeout|0/1|900|0|—|
|grok-4.7-medium|timeout|0/1|180|0|—|

Nos 8 timeouts, "0/1" vem de um erro na coleta: `ModuleNotFoundError: No module named 'telefones'`.

## 2. O que os Gemini entregaram
Nos 4 Gemini, tanto na execução de 180 s (backup) quanto na de 420 s:
- `codigo/` contém só `.gitkeep` e `enunciado.md`, idêntico ao da tarefa.
- Não há `telefones.py` nem `SUPOSICOES.md`.
- `agente_stdout.txt` e `agente_stderr.txt` estão vazios (0 bytes).

O `agy` só escreve no log ao terminar. Por isso não dá para ver onde o agente travou: o processo foi morto (exit -9) sem ter gravado nenhum arquivo. O 0% vem daí: os testes ocultos não encontram o módulo.

Os 4 Grok mostram o mesmo padrão: o log registra uma única frase ("Vou ler o enunciado…") e nenhum arquivo é gravado. Os mesmos 8 modelos tiram 8,6 a 9,7 em 10-ambigua-codex, -gemini e -grok.

Em todo o run-1 há 30 timeouts com `codigo/` vazio. 8 deles são desta tarefa (8 de 8 possíveis); nenhuma outra tarefa passa de 3.

## 3. A tarefa em si
- O enunciado é claro: nomeia o arquivo (`telefones.py`), as assinaturas das duas funções e o `SUPOSICOES.md`, e pede só a biblioteca padrão.
- `meta.yaml` declara `arquivos_solucao` (`telefones.py` e `SUPOSICOES.md`).
- O `conftest.py` põe o diretório de trabalho no `sys.path`. Não há fixture externa nem dependência fora da stdlib.
- Testes ocultos rodados em /tmp: a referência passa 41/42, e a solução do gpt-6.1-sol-high também passa 41/42. Nos dois casos a única falha é `test_suposicoes_md_existe`, porque copiei só o `.py`. Com o `SUPOSICOES.md`, a sol-high fez 42/42 no oficial. Isso confirma que os testes funcionam.
- O teste de volume (5000 telefones) roda em menos de 0,1 s.
- Nada exige algo que só a Claude adivinharia: o Codex, que não é a autora, fez 40 a 42 de 42.

## Conclusão: SEM DEFEITO NA TAREFA (falha dos modelos; causa do travamento inconclusiva)
- Enunciado, conftest e testes ocultos estão corretos. A referência e uma solução de outra empresa passam (42/42 com `SUPOSICOES.md`).
- Os 4 Codex resolveram a tarefa (40 a 42 de 42), sem ser a empresa autora.
- Gemini e Grok, 8 de 8, morrem por timeout sem gravar nenhum arquivo, nem com 420 s ou 900 s.
- O padrão é específico desta tarefa, mas os logs vazios impedem ver a causa. PALPITE: o agente fica deliberando sobre as ambiguidades e não grava nada antes do kill.
- Se quiserem entender a causa, o próximo passo seria rodar 1 Gemini com o log em streaming. Não fiz isso.
