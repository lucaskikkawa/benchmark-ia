# Site 1.0 (v3): como gerar, verificar e plugar a rodada v3

O site v2 (`site/index.html`, `site/app.html`, `site/build_site.py`) **não muda**. Tudo do v3 mora aqui:

| arquivo | o que é |
|---|---|
| `app.html` | fonte do site (HTML + CSS + JS), com 3 marcas que o build substitui: `/*__FONTES__*/`, `__DADOS__`, `__DADOS_V3__` |
| `build_v3.py` | gera `index.html` autocontido (fontes em base64, dados embutidos), com as conferências da Rodada 1 |
| `index.html` | **o site** (arquivo único, abre offline) |
| `verificar_v3.js` | QA no Chrome headless (desktop 1280 px e celular 390×844); prints em `qa/` |
| `qa/mock/index-mock.html` | site com dados v3 **falsos**, só para testar o caminho de plugar (nunca publicar) |

## Gerar e verificar

```sh
python3 site/v3/build_v3.py          # gera site/v3/index.html
python3 site/v3/build_v3.py --mock   # gera site/v3/qa/mock/index-mock.html (QA)
node site/v3/verificar_v3.js         # tem de terminar com "TUDO OK"
```

## Onde fica o bloco v3

Dentro de `index.html`, logo depois do bloco `<script id="dados">` (Rodada 1, não mexer):

```html
<script id="dados-v3" type="application/json">
{ "status": "aguardando rodada v3", "motivo": "...", "modelos": [...], "runsA": [], "runsB": [] }
</script>
```

Enquanto `status` for `"aguardando rodada v3"`, o teste novo mostra Claude e Codex (as mesmas tentativas da Rodada 1)
e Hydrogen/Neon aparecem com ⏳ "aguardando rodada v3" no ranking, no Comparar, no Esforço, no Mapa e no card
"Gemini antigo × Gemini novo".

## Como plugar os números (3 jeitos)

**1. Automático (recomendado).** Quando o Avaliador terminar a rodada v3, as avaliações ficam em
`resultados/gemini/gemini-4-{hydrogen,neon}-{medium,high}/<tarefa>/run-1/avaliacao_avaliador.json`
(mesmo formato da Rodada 1). Basta rodar `python3 site/v3/build_v3.py` de novo. O build:
- exige as 30 tarefas por versão e nenhuma tarefa `*-gemini` (para com erro se faltar);
- monta o prazo normal (Ranking A) com `nota_final_10` (timeout = 0);
- monta o prazo estendido (Ranking B) trocando cada timeout pelo `avaliacao_avaliador_7min.json` da mesma pasta.
  Se algum timeout não tiver o arquivo de 7 min, o v3 fica **sem** prazo estendido (o botão desliga nele) e o
  build avisa. O site abre no prazo normal (`MANCHETE='A'` em `app.html`, item 8 de `planejamento/decisoes-v3.md`),
  então a falta do B não muda a abertura; só o botão "Prazo estendido" fica desligado no v3.
- Pasta diferente: `python3 site/v3/build_v3.py --v3-dir OUTRA/PASTA` (procura `OUTRA/PASTA/gemini/<versão>/`).

**2. A partir de um JSON pronto:** `python3 site/v3/build_v3.py --v3-json arquivo.json`, no formato abaixo.

**3. À mão, sem rebuild:** trocar o conteúdo de `<script id="dados-v3">` no `index.html` por um JSON no formato
abaixo. O site valida no navegador; versão com problema fica "aguardando" e o problema aparece no aviso do topo
e em Mais → Técnico → "Bloco de dados v3".

### Formato

```json
{
  "status": "ok",
  "modelos": ["gemini-4-hydrogen-medium", "gemini-4-hydrogen-high", "gemini-4-neon-medium", "gemini-4-neon-high"],
  "runsA": [
    {"m": "gemini-4-hydrogen", "x": "medium", "t": "01-funcao-claude", "s": "ok", "d": 132.4,
     "p": 100.0, "tp": 12, "tt": 12, "rb": 9.1, "j": {"claude": 9.0, "codex": 9.2},
     "ji": {"claude": [2,2,2,1,2], "codex": [2,2,2,2,1]}, "n": 9.73}
  ],
  "runsB": [ { "...mesmos campos, sem n...": "", "ni": 9.73, "nii": 9.73, "rf": 0 } ]
}
```

- `m` modelo, `x` esforço, `t` tarefa (nunca `*-gemini`), `s` `"ok"` ou `"timeout"`, `d` segundos,
  `p` % de testes (0–100), `tp`/`tt` testes passados/total, `rb` rubrica 0–10 (ou `null` no timeout),
  `j` nota de cada juiz, `ji` os 5 itens (0–2) de cada juiz.
- `n` (A) = nota oficial; `ni` (B) = nota com timeout = 0; `nii` (B) = 0,7·p/10 + 0,3·rb; `rf` = 1 se foi refeita com 7 min.
- Cada versão precisa de **30** tentativas, uma por tarefa. `runsB` pode ficar `[]` (sem prazo estendido).
- `status` começando com `MOCK` mostra a faixa vermelha "dados de teste".

Depois de plugar, rode `node site/v3/verificar_v3.js`. Os testes de "aguardando" vão falhar de propósito
(o placeholder sumiu); ajuste-os para os números reais e confira os prints em `qa/`.

## Decisões (item 8 de `planejamento/decisoes-v3.md`, 25/11)

- Manchete: `MANCHETE='A'` em `app.html` (abre em v3 + prazo normal, mesmo limite para todos); 7 min fica como "Prazo estendido".
- Texto do motivo da saída do Grok (Mais → "Por que o Grok saiu"): aprovado.
- Empate técnico: regra simples `TIE=0.30` em `app.html` (o bootstrap pareado sugerido pelo Opus não foi feito).
- Média por empresa: mesmo método do `resultados/RODADA.md` nos dois prazos e nos dois testes (média de cada versão
  arredondada em 2 casas, depois média simples das versões). Rodada 1: A = Claude 9,62 · Codex 8,76 · Gemini 4,58;
  B = 9,71 · 9,29 · 7,63 (o `RELATORIO_7MIN.md`, que não arredonda as versões, mostra Codex 9,30).
