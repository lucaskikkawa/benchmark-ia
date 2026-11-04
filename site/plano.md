# Plano — site "Rodada 1" do benchmark

Um único `index.html` (HTML + CSS + JS + dados embutidos, sem CDN obrigatório), mobile-first (base 390 px, cresce até ~1100 px em 2 colunas). Visual de desenho animado: contorno grosso, sombras "carimbadas", um mascote-robô por empresa (cara de terminal `>_`). Tudo que é número é **recalculado no navegador** a partir das execuções brutas, de modo que sliders e toggles mudam o ranking ao vivo.

Mocks de todas as abas (390×844, Chrome headless, números reais de `resultados/`): `mock-ranking`, `mock-comparar`, `mock-esforco`, `mock-tarefas`, `mock-juizes` (`.html` → `.png`), gerados por `site/gerar_mocks.py` (rodar na raiz do repo). O antigo `mock.html`/`mock.png` (mascotes da 1ª versão) ficou obsoleto: `mock-ranking` o substitui.

---

## 1. Dados: de onde vem cada número

### 1.1 Fonte primária (por execução, 528 linhas)

Um script de build (`scripts/gerar_site_dados.py`, a escrever) varre `resultados/[cg]*/*/*/run-*/` (o mesmo glob de `scripts/rodada_relatorio.py`, então o piloto fica de fora) e gera um JSON compacto que é colado em `<script id="dados" type="application/json">` no HTML.

| Campo no site | Arquivo | Campo concreto |
|---|---|---|
| empresa | `resultado.json` | `empresa` (claude/codex/gemini/grok) |
| modelo | `resultado.json` | `modelo` (ex.: `claude-haiku-5-5`) |
| esforço | `resultado.json` | `esforco` (`medium`/`high`) |
| tarefa, tipo, autora | `resultado.json` | `tarefa` (ex.: `04-dados-grok`) → tipo = `tarefa[:2]` + nome, autora = sufixo; conferir com `avaliacao.json.autora` |
| run | `resultado.json` | `run` (1 em 480 execuções; 2–4 só na tarefa de consistência) |
| status | `resultado.json` | `status` (`ok` 372 / `timeout` 133 / `erro` 23) |
| tempo | `resultado.json` | `duracao_agente_s` |
| testes | `resultado.json` | `testes_passados`, `testes_total`, `pct_passados` |
| horário | `resultado.json` | `inicio_iso` (19:07 de 29/10 → 01:27 de 30/10, BRT) |
| rubrica final | `avaliacao.json` | `rubrica_10` (`null` → 0, como em `rodada_relatorio.py`) |
| nota de cada juiz | `avaliacao.json` | `juizes.<empresa>.rubrica_10` e `.modelo` (`null` = juiz falhou) |
| itens da rubrica (0–2 cada) | `avaliacao.json` | `juizes.<empresa>.itens.{legibilidade, erros_bordas, idiomatico, manutenibilidade, documentacao_instrucoes}` |
| ocorrências dos juízes | `avaliacao.json` | `obs[]` (ex.: "grok tentativa 1 falhou: JSON inválido", "só 1 juiz válido…") |
| tamanho do código (opcional) | pasta `codigo/` | soma dos `.py`, igual a `r['src']` no script |
| teto de tempo | `tarefas/<tarefa>/meta.yaml` | `timeout_min` (3 min em 31 tarefas, 5 min em 9) |
| motivo do erro | `run-*/agente_stdout.txt` / `agente_stderr.txt` | grep de `402 … balance exhausted` / `session limit`, gravado como `erro_cota: true` |

**Não usar** `avaliacao.json.nota_final_10`: esse campo **não aplica a penalidade de timeout** (ex.: `claude-opus-5-5-high/05-cli-gemini/run-1` é timeout e tem 10.0). O site recalcula a nota.

Formato embutido (~40 KB): `{"e":"claude","m":"claude-haiku-5-5","x":"high","t":"01-funcao-codex","r":1,"s":"ok","d":26.4,"p":100,"tp":25,"tt":25,"rb":10,"j":{"gemini":10,"grok":10},"ji":{...},"q":0,"lim":3}`.

### 1.2 Fórmula (idêntica a `rodada_relatorio.py`, linhas 11–12)

```
sem_pen = w·pct_passados/10 + (1−w)·rubrica      // w = peso dos testes (padrão 0,7)
nota    = (penalidade ligada && status=='timeout') ? 0 : sem_pen
média do modelo×esforço = média simples de todas as execuções dele (N = 33, como em RODADA.md)
```

Teste de aceitação: com w = 0,7 e penalidade ligada o site tem de reproduzir **exatamente** as colunas "Nota" e "Nota s/ pen." da tabela "Ranking modelo × esforço" de `RODADA.md` (9.76, 9.71, 9.68 … 1.19). Um `console.assert` no carregamento compara com esses valores fixos.

### 1.3 Fonte secundária (textos e conferência)

| Bloco do site | Origem |
|---|---|
| Frase da fórmula, ressalvas (cota, 133 timeouts, máquina pausada 20:52–0:54) | `RODADA.md` → cabeçalho e "Ressalvas importantes" (texto copiado no build) |
| "Tarefas que todos gabaritaram" | `RODADA.md` → seção "Tarefas em que todos tiraram 100%" (e recalculado: todas as execuções com `pct_passados == 100`) |
| Mutation score (tipo 08) | `RODADA.md` → "Mutation score": só nota explicativa, sem número |
| Linha do tempo da noite | `rodada.log` (linhas `INICIO`/`FIM … status= testes= agente=`); opcional, dá para tirar só de `inicio_iso` + `duracao_agente_s` |
| Piloto (rodapé, "como começou") | `piloto/PILOTO.md` (tabela de 16 linhas) |

---

## 2. Seções (ordem de rolagem no celular)

Navegação: barra fixa embaixo com 5 ícones grandes (🏆 Ranking · ⚖️ Comparar · 🔥 Esforço · 🧩 Tarefas · 🧑‍⚖️ Juízes) que rolam até a seção; no desktop vira barra no topo.

### 2.0 Capa
- Título "Rodada 1" em balão de fala, os 4 robôs enfileirados, com o `>` virado para o campeão.
- Três contadores animados (contam de 0 ao valor ao entrar na tela): **528 execuções**, **133 timeouts**, **23 erros**. Origem: contagem de `status`.
- Linha: "16 modelos×esforço · 40 tarefas · 4 empresas · 29/10 19:07 → 30/10 01:27".

### 2.1 Ranking ao vivo (a peça central)
- **Cartão de controles** (fica *sticky* logo abaixo do topo enquanto a lista está visível):
  - Slider **Testes ⟷ Rubrica** (0–100 %, passo 5, padrão 70/30). O polegar é um botão neutro (lâmpada), fora das cores das empresas. Dois rótulos mostram "70 % testes · 30 % rubrica" em tempo real.
  - Toggle **"Timeout vale zero"** (padrão ligado). Desligado = "Nota s/ pen.".
  - Toggle extra **"Ignorar erros de cota"** (padrão desligado): remove as 23 execuções `erro` (16 do grok-4.7-high, 7 do claude-opus-5-5-high) do denominador. Justificativa: ressalva de `RODADA.md`.
  - Chip **"Só run-1"** (padrão desligado): usa só as 480 execuções `run == 1`, tirando o peso extra da tarefa de consistência (N passa de 33 para 30).
  - Botão "↺ padrão do relatório".
- **Lista de 16 linhas**, cada uma: posição, robô da empresa, nome do modelo, chip de esforço (medium = cor cheia, high = hachurado), barra horizontal 0–10 e a nota com 2 casas.
  - Reordenação animada (FLIP, 400 ms, com leve "quique"). Quem sobe ganha uma setinha verde ▲n, quem desce, uma vermelha ▼n, comparando com o padrão do relatório.
  - Quem chega ao 1º lugar ganha uma coroa e uma chuva rápida de confete (respeita `prefers-reduced-motion`).
  - Tocar na linha abre a ficha do modelo (2.2) já com ele selecionado.
- **Exemplos que o leitor descobre mexendo** (conferidos nos dados):
  - Penalidade desligada → gemini-4-argon-medium vai de 7.37 para 8.69 e grok-4.7-build-fast-medium de 7.00 para 8.73, ambos passando gpt-6.1-sol-high.
  - Slider em 0 % testes (só rubrica) e sem penalidade → grok-4.7-build-fast-medium (7.85) sobe para o 4º lugar, à frente de todos os modelos do Codex (gpt-*).
  - Slider em 100 % testes → claude-opus-5-5-medium empata com o haiku-high em 10.00.
  - "Ignorar erros de cota" ligado → claude-opus-5-5-high pula de 7.62 (8º) para 9.30 (N = 26); grok-4.7-high só vai de 1.22 para 2.26 (N = 17), porque também tem 13 timeouts.
  - Uma faixa embaixo da lista mostra uma dessas "curiosidades" conforme o estado.

### 2.2 Ficha e duelo de modelos ("Comparar")
- Dois seletores (A × B) em formato de cartas; padrão: claude-haiku-5-5-high × gpt-6-luna-medium.
- **Gráfico de radar** com 5 eixos (média dos `itens` da rubrica, 0–2, entre os juízes válidos) + 2 eixos extras opcionais: %testes e "pontualidade" (1 − taxa de timeout); todos normalizados para 0–100 % (itens ÷ 2). Polígono A sólido, B tracejado com contorno tinta (o cinza do Codex sozinho não aparece no branco), cada um com a cor da empresa.
- **Barras espelhadas por tipo de tarefa** (01-funcao … 10-ambigua): A para a esquerda, B para a direita, nota com o peso/penalidade atuais. O vencedor de cada linha ganha uma estrelinha.
- Mini-placar: "A vence em 6 de 10 tipos". Tempo médio A × B como dois relógios.
- Tocar numa barra lista as execuções daquele tipo (status, testes x/y, tempo, nota de cada juiz).

### 2.3 Medium vs high ("Mais esforço ajuda?")
- **Gráfico de halteres** (dumbbell), 8 linhas (uma por modelo): bolinha cheia = medium, bolinha hachurada = high, linha entre elas verde se high > medium e vermelha se pior. Origem: mesma média de 2.1 (reage ao slider e ao toggle).
- Valores do relatório (padrão): só claude-haiku-5-5 melhora (+0.06); grok-4.7 cai 5.18; grok-4.7-build-fast cai 3.50; claude-opus-5-5 cai 2.06 (maior parte por erro de cota, e o toggle "Ignorar erros de cota" mostra isso ao vivo).
- Segundo gráfico pequeno: tempo médio medium → high (seta), ex.: luna 20 s → 32 s, grok-4.7 145 s → 101 s (cai porque os erros de cota terminam rápido).
- Selo de veredito com o robô: "High piorou em 7 de 8 modelos 😬".

### 2.4 Mapa de tarefas (tipo × empresa)
- **Heatmap 10 × 4** (linhas = tipo, colunas = empresa resolvedora), escala sequencial de uma cor só (amarelo claro → azul-tinta), número dentro da célula. Reage aos controles.
- Alternador de agrupamento das colunas: "empresa resolvedora" | "modelo×esforço (16 colunas, rolagem horizontal)" | "empresa **autora** da tarefa" (quem escreveu tarefas mais difíceis?).
- Destaques: 08-testes (claude 9.85 × gemini 0.83 × grok 0.87) e 10-ambigua (único tipo em que codex 9.36 passa claude 7.50).
- Faixa "Todo mundo gabaritou": 01-funcao-gemini e 02-bug-codex; e as 8 "quase".
- Tocar numa célula mostra as execuções dela.

### 2.5 Consistência (4 runs da mesma tarefa)
- Para cada modelo×esforço, **4 bolinhas** (runs 1–4) da tarefa 04-dados-claude (claude usa 04-dados-grok), em fila: cheia = nota, vazia com ⏱ = timeout, vazia com ⚠ = erro.
- Ordenado por desvio padrão. Destaque: claude-opus-5-5-high "10, 0, 0, 0" (erros de cota) e as execuções "8.8, 0, 0, 0" de grok/gemini (timeout).
- Origem: execuções com `run` 1–4 dessa tarefa; confere com a tabela "Consistência" de `RODADA.md`.

### 2.6 Os juízes ("Tribunal")
- Quatro robôs de toga lado a lado, cada um com a **nota média que deu**: claude 6.87 (n=211), codex 6.15 (n=276, o mais severo), gemini 6.97 (n=222), grok 8.56 (n=154, o mais bonzinho). Origem: média de `juizes.<e>.rubrica_10` não nulos.
- **Barras empilhadas de falhas** por juiz: JSON inválido × timeout (contagem a partir de `obs[]`; tem de bater com "Falhas de juiz" de `RODADA.md`: grok 212 JSON + 13 timeout, gemini 130 timeout, claude 66 JSON).
- **Dispersão** juiz 1 × juiz 2 nas 344 execuções com dois juízes válidos (diagonal = acordo). Destaque das 5 com diferença > 3 pts. Hover/toque mostra a execução.
- Toggle de "corrigir viés": subtrai de cada juiz a média dele e soma a média geral antes de calcular a rubrica. Afeta o ranking de 2.1 (reaproveita os mesmos dados de `j`). Marcado como "experimento, não é o critério oficial".

### 2.7 A noite da rodada (opcional, se sobrar tempo)
- Linha do tempo horizontal de 19:07 a 01:27 com uma faixa por empresa; cada execução é um tracinho do `inicio_iso` até `inicio_iso + duracao_agente_s`, colorido por status. Faixa cinza com lua 🌙 marcando a pausa da máquina (20:52–0:54, de `RODADA.md`).

### 2.8 Rodapé "Letras miúdas"
- Fórmula, critério de timeout (`timeout_min` de `meta.yaml`, 3 ou 5 min), as ressalvas de `RODADA.md`, link para baixar o JSON embutido (`Blob` + download) e tabela completa (acessibilidade: todo gráfico tem um "ver como tabela").

---

## 3. Interações: resumo técnico

| Interação | Estado | O que recalcula |
|---|---|---|
| Slider testes/rubrica | `w ∈ [0,1]` | 2.1, 2.2, 2.3, 2.4, 2.5 |
| Toggle timeout = 0 | `pen: bool` | idem |
| Ignorar erros de cota | `semCota: bool` | idem |
| Só run-1 | `soRun1: bool` | idem (2.5 ignora) |
| Corrigir viés dos juízes | `vies: bool` | rubrica de todas as execuções |
| Seleção A × B | `a, b` | 2.2 |
| Filtro de empresa (chips no topo do ranking) | `empresas: Set` | 2.1 |

- Estado único `S` + função pura `media(execucoes, S)`; cada seção tem `render(S)`. Mudanças em `requestAnimationFrame`, sem framework.
- Estado vai para o `location.hash` (`#w=50&pen=0`) → dá para mandar um link com "o meu ranking".
- Gráficos em **SVG feito à mão** (nada de biblioteca; mantém o arquivo único e offline). Todos com tooltip ao toque (alvo ≥ 44 px), legenda e rótulo direto; nenhum depende só da cor.
- Acessibilidade: slider é `<input type="range">` estilizado, toggles são `<button role="switch" aria-checked>`; `aria-live="polite"` anuncia "claude-haiku-5-5-high continua em 1º".
- Tamanho-alvo: < 250 KB com as fontes em subset.

---

## 4. Estética

### 4.1 Linguagem
Desenho animado "adesivo": todo bloco tem **contorno de 3 px** na cor tinta, cantos de 18–22 px, e **sombra dura deslocada** (`box-shadow: 4px 4px 0 #2B2340`, sem desfoque). Botões "afundam" ao toque (sombra vai a 0 e o bloco desce 3 px). Fundo creme com bolinhas suaves (padrão SVG em 6 % de opacidade). Títulos levemente inclinados (−2°) dentro de faixas de cor. Números grandes com contorno.

### 4.2 Paleta

| Papel | Hex | Uso |
|---|---|---|
| Fundo | `#FFF8EC` | creme |
| Cartão | `#FFFFFF` | superfície dos cartões |
| Tinta (texto e contorno) | `#2B2340` | texto principal, contornos, sombras |
| Texto secundário | `#6B6280` | legendas |
| Destaque | `#FFD23F` | faixas de título, polegar do slider, coroa |
| Destaque 2 | `#FF9F1C` | botões ativos |
| **claude** | `#E06A1E` | laranja |
| **codex** | `#C3C8D0` | cinza-claro |
| **gemini** | `#3B6FE0` | azul |
| **grok** | `#1C1B22` | preto |
| Melhorou ▲ | `#2FB86B` | só setas/indicadores, sempre com ícone |
| Piorou ▼ / timeout | `#E5484D` | idem, com ⏱ |
| Erro de cota | `#8A8FA3` | cinza com ⚠ |
| Heatmap (sequencial) | `#FFF3C4 → #FFD23F → #3B9C9C → #2B2340` | uma rampa, claro = pior |

Paleta das empresas conferida com o validador da skill de dataviz (fundo `#FFF8EC`, todos os pares): separação para daltonismo **passa** com folga (pior par codex↔claude, ΔE 21,6 deutan; visão normal ΔE 25,0). **Falham por definição** a faixa de luminosidade e o croma mínimo: cinza-claro e preto são neutros por escolha (cor pedida para Codex e Grok); e o cinza-claro tem contraste 1,6:1 com o fundo (aviso). Compensação obrigatória: toda marca de dado tem **contorno de 2–3 px na cor tinta** (é ele que dá o contraste, não o preenchimento), a cor **nunca anda sozinha** (sempre robô + nome), high usa hachura (45°) e todo gráfico tem "ver como tabela". O laranja do Claude é `#E06A1E` porque um laranja mais claro (`#E8762D`) ficava em 2,8:1 no creme; esse passa 3:1. Na hachura sobre o preto do Grok o traço é claro (`rgba(255,255,255,.5)`).

### 4.3 Fontes
- Títulos e números: **Fredoka** (600/700), arredondada, cara de desenho.
- Texto e rótulos: **Nunito** (400/700/800), com `font-variant-numeric: tabular-nums` nas notas para não "tremer" durante a animação.
- Arquivo único: subset (latim + dígitos + ▲▼⏱⚠) com `pyftsubset` e embutido como `woff2` em base64 (~30 KB cada). Plano B: `<link>` do Google Fonts com `font-display: swap` e fallback `ui-rounded, "Comic Relief", system-ui`.

### 4.4 Mascotes: robôs-terminal (SVG inline, originais; não usar logos das empresas)

Todos são o **mesmo robô** no espírito de um ícone de terminal: cabeça quadrada de cantos arredondados (`rect` 30×25, `rx` 7, contorno 2,5 px tinta), com o rosto feito só de **`>`** (olho/prompt) e **`_`** (boca/cursor). Muda a cor da cabeça e um acessório no topo, para que a empresa seja reconhecível também sem cor (daltonismo, impressão).

| Empresa | Robô | Cabeça | Rosto `>_` | Acessório (identidade sem cor) |
|---|---|---|---|---|
| claude | **Clô** | laranja `#E06A1E` | tinta `#2B2340` | antena com faísca amarela de 4 pontas |
| codex | **Códi** | cinza-claro `#C3C8D0` | tinta `#2B2340` | antena de bolinha amarela + "orelhas" laterais escuras |
| gemini | **Gêmi** | azul `#3B6FE0` | branco | **duas** antenas (as "gêmeas"), pontas azul-claras |
| grok | **Gróqui** | preto `#1C1B22` | branco | sem antena: viseira cinza no topo + parafusos amarelos nas laterais |
| juízes | os mesmos 4 de **toga** (manto tinta com gola branca) | — | — | martelinho bate quando a seção aparece |

Expressões (trocadas pela nota ≥ 8 / 5–8 / < 5 e por status), sempre mantendo `>` e `_`:
- **feliz**: `_` pisca como cursor (1 s) e o brilho no canto da cabeça acende; 1º lugar ganha coroa 👑.
- **neutro**: `>_` parado.
- **triste**: `>` cai 15° e o `_` vira `…`.
- **timeout**: o `_` vira uma ampulheta ⏱ piscando.
- **erro de cota**: `>` fecha (vira `-`) e sai um "Zzz" ("session limit" / "402 balance exhausted").

Cada robô é um `<symbol>` de < 1 KB (`#m-claude`, `#m-codex`, `#m-gemini`, `#m-grok`, mais `#toga`); o SVG de referência está em `gerar_mocks.py` (`robo()`/`SYMBOLS`). Animações em CSS: balanço em repouso (`rotate ±3°`, 3 s), pulo quando sobe no ranking, tudo desligado com `prefers-reduced-motion`.

### 4.5 Layout mobile-first
- Base 390 px: uma coluna, margens de 16 px, cartões em largura cheia, controles com ≥ 44 px de altura.
- ≥ 768 px: controles numa coluna lateral fixa à esquerda, ranking à direita; 2.2 e 2.3 lado a lado.
- Modo escuro (`prefers-color-scheme`): fundo `#1E1A2E`, cartões `#2B2540`, contorno vira `#0E0B18`, e as cores das empresas são revalidadas no validador contra o fundo escuro antes de entrar. O robô preto do Grok some no fundo escuro (contraste 1,0:1): lá o contorno dele vira `#E9E6F2` e as barras do Grok ganham borda clara.

---

## 5. Etapas de construção (próxima fase, não feita agora)

1. `scripts/gerar_site_dados.py` → `site/dados.json` + checagem contra `RODADA.md` (todas as tabelas).
2. Esqueleto HTML/CSS com tokens da seção 4 + robôs SVG (reaproveitar os `<symbol>` de `gerar_mocks.py`).
3. Motor `media()` + ranking ao vivo (2.1) com FLIP.
4. Seções 2.3 → 2.4 → 2.2 → 2.6 → 2.5 → 2.7.
5. Build final: inline de dados, fontes e SVG em `site/index.html`; screenshots em 390×844 e 1280×800; teste de `prefers-reduced-motion` e daltonismo (emulação do Chrome DevTools).

---

# Versão 2 — dois rankings oficiais + QA (decidido em 04/11/2026)

> A versão 1 acima fica preservada como foi feita. Esta seção descreve só o que muda na v2.

## V2.1 Fonte única das notas
- Todas as notas vêm do **Bench - Avaliador** (2 juízes neutros, auditadas). Não usar `avaliacao.json` antigos.
- **Ranking A — limite original (3/5 min):** `resultados/_avaliador/notas_avaliador.csv` (16 combinações, N=30, com Grok e penalidades do grok-4.7-high).
- **Ranking B — limite de 7 min (420 s):** `resultados/_avaliador/cenario_7min/` (`notas_7min.csv`, `matriz_7min.csv`, `resumo_7min.json`). São 12 combinações, sem o Grok. Os 70 timeouts de Claude, Codex e Gemini foram refeitos com 420 s.
  - `nota_i` (padrão no site): timeout = 0.
  - `nota_ii` (toggle): entrega parcial de timeout é julgada.
- O `build_site.py` valida os dois rankings contra o relatório e o `resumo_7min.json` e para com erro se algo não bater.

## V2.2 O que muda no site
- Um seletor bem visível entre **Ranking A (3 min)** e **Ranking B (7 min)**, com um texto curto explicando a diferença.
- Toggle `nota_i`/`nota_ii` só no Ranking B.
- A seção "Mais esforço ajuda?" mostra o high − medium dos dois rankings lado a lado. A conclusão: com 7 min o high empata ou ganha no Claude e no Codex; no argon só ganha julgando a entrega; o flash-high continua pior.
- Tarefa **10-ambigua-claude**: o 0% continua na nota, com a marcação "timeout sem entrega (Gemini e Grok); tarefa validada". Os 4 Codex resolvem com 40 a 42 de 42 testes, e a análise está em `resultados/_avaliador/analise_10_ambigua_claude.md`.
- As penalidades do grok-4.7-high continuam com o selo ⚖️, só no Ranking A.
- Visual, mascotes e abas da v1 continuam iguais.

## V2.3 Fluxo de construção + QA
1. O **Bench - Claude** gera o site e os prints, sem commit.
2. O **Bench - Gemini** faz o QA com o Gemini 3.8 Flash (esforço medium): abas, console, toggles, números contra os CSVs do Avaliador e layout no celular (390×844). Devolve uma lista de erros.
3. Uma volta é o Claude fazer e o Gemini avaliar. São **no máximo 3 voltas**. Se ainda sobrar erro, o Chefe leva ao Lucas.
4. O site só vai ao Lucas depois de passar no QA. O commit na `rodada-1` (PR #6) vem depois.
5. Os bots falam entre si sem acordar (priority false); só o Avaliador pode ser acordado.

## V2.4 Fora do escopo do site da rodada 1
- A próxima rodada (sem Grok e com limite padrão de 420 s em todas as tarefas) é outra conversa.
