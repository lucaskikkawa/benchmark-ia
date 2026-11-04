"""Consolida auditoria + avaliacao_avaliador.json -> grava incoerências em cada avaliacao_avaliador.json e gera
resultados/RELATORIO_AVALIADOR.md e resultados/_avaliador/notas_avaliador.csv. Não toca avaliacao.json/resultado.json."""
import json, pathlib, statistics as st, collections, csv, re
ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "resultados"; AV = RES / "_avaliador"
aud = {x["pasta"]: x for x in json.load(open(AV / "auditoria.json"))}
GH = "resultados/grok/grok-4.7-high/"
if (AV / "auditoria_grok_high.json").exists():
    aud.update({x["pasta"]: x for x in json.load(open(AV / "auditoria_grok_high.json"))})
ESPECIAIS = {GH + t for t in ["07-performance-claude/run-1", "06-multiarquivo-codex/run-1", "09-api-gemini/run-1", "08-testes-claude/run-1",
             "08-testes-codex/run-1", "08-testes-gemini/run-1", "09-api-claude/run-1", "09-api-codex/run-1", "10-ambigua-claude/run-1",
             "10-ambigua-gemini/run-1", "04-dados-claude/run-2", "04-dados-claude/run-3", "04-dados-claude/run-4"]}
PRIMEIRA = {GH + t for t in ["07-performance-claude/run-1", "06-multiarquivo-codex/run-1", "09-api-gemini/run-1"]}
import subprocess, hashlib
def sem_entrega(pasta, tarefa):
    ini = ROOT / "tarefas" / tarefa / "inicial"
    h = lambda f: hashlib.md5(f.read_bytes()).hexdigest()
    for f in (ROOT / pasta / "codigo").rglob("*"):
        if not f.is_file() or "__pycache__" in f.parts or f.name in ("enunciado.md", ".gitkeep"): continue
        o = ini / f.relative_to(ROOT / pasta / "codigo")
        if not o.exists() or h(o) != h(f): return False
    return True
def antiga_head(pasta):
    try:
        r = json.loads(subprocess.run(["git", "show", f"HEAD:{pasta}/resultado.json"], cwd=ROOT, capture_output=True, text=True).stdout)
        a = json.loads(subprocess.run(["git", "show", f"HEAD:{pasta}/avaliacao.json"], cwd=ROOT, capture_output=True, text=True).stdout or "{}")
    except ValueError:
        return None
    if r["status"] == "timeout": return 0.0
    return a.get("nota_final_10") if a.get("nota_final_10") is not None else round(0.7 * r["pct_passados"] / 10, 2)

def classifica(i):
    if "avaliacao_avaliador.json" in i and "não commitadas" in i:
        return None
    if "98a25b8" in i:
        return "resultado.json da rodada sobrescreveu o do piloto (commit 98a25b8 'Piloto') no mesmo caminho run-1; o piloto está em resultados/piloto. Benigno, mas o histórico do arquivo mistura duas execuções"
    if "b850e82" in i:
        return "execução refeita (commit b850e82 'Refaz 7 execuções do opus-5-5-high que falharam por cota'; backup em resultados/_erros_cota). Documentada no commit"
    return i

rows = []
for p, a in aud.items():
    f = ROOT / p / "avaliacao_avaliador.json"
    if not f.exists():
        continue
    av = json.load(open(f))
    inc = [c for c in (classifica(i) for i in a["incoerencias"]) if c]
    rr = a.get("rerun") or {}
    av["reexecucao_testes"] = rr
    av.pop("nota_ajustada_por_reexecucao", None)
    if rr.get("total") and (rr["total"], rr["passados"]) != (a["testes_total"], a["testes_passados"]) and av["status"] != "timeout":
        # falha não reproduzida: teste flaky do harness. Usa a reexecução e registra.
        pct = 100.0 * rr["passados"] / rr["total"]
        av["pct_testes"] = round(pct, 2); av["testes_passados"] = rr["passados"]; av["testes_total"] = rr["total"]
        if av.get("rubrica_media_10") is not None:
            av["nota_final_10"] = round(0.7 * pct / 10 + 0.3 * av["rubrica_media_10"], 2)
        av["nota_ajustada_por_reexecucao"] = True
    if av["status"] == "timeout" and a["pct"] > 0:
        inc.append(f"timeout com entrega parcial: {a['testes_passados']}/{a['testes_total']} testes passam ({a['pct']:.0f}%), mas a regra zera a nota")
    av["incoerencias"] = inc
    av["nota_antiga_avaliacao_json"] = a["nota_antiga"]
    av["nota_antiga_com_penalidade"] = antiga_head(p) if p.startswith(GH) else 0.0 if av["status"] == "timeout" else (a["nota_antiga"] if a["nota_antiga"] is not None else round(0.7 * a["pct"] / 10, 2))
    for k in ("nota_cenario_A", "nota_cenario_B"): av.pop(k, None)
    if p in ESPECIAIS:
        dur = av["duracao_agente_s"] or 0
        if sem_entrega(p, av["tarefa"]):
            fator, regra = 0.0, "sem entrega (codigo/ igual ao inicial): zero"
        elif av["status"] == "timeout" or dur > 900:
            fator, regra = 0.5, f"estourou 900 s ({dur:.0f} s): entrega incompleta avaliada, ×0,5"
        elif p in PRIMEIRA: fator, regra = 1.0, f"1ª tentativa, {dur:.0f} s (≤300 s): nota cheia"
        elif dur > 600: fator, regra = 0.5, f"2ª tentativa, {dur:.0f} s (600–900 s): ×0,5"
        else: fator, regra = 0.7, f"2ª tentativa, {dur:.0f} s (≤600 s): ×0,7"
        base = round(0.7 * av["pct_testes"] / 10 + 0.3 * av["rubrica_media_10"], 2) if av.get("rubrica_media_10") is not None else (0.0 if fator == 0 else None)
        av["regra_excepcional_grok_4_7_high"] = {"nota_base": base, "fator": fator, "regra": regra}
        av["nota_final_10"] = round(base * fator, 2) if base is not None else None
    json.dump(av, open(f, "w"), ensure_ascii=False, indent=1)
    av["combo"] = a["combo"]
    rows.append(av)

def m(xs):
    xs = [x for x in xs if x is not None]
    return round(st.mean(xs), 2) if xs else None
def fmt(x): return "—" if x is None else f"{x:.2f}"
def d(a, b): return "—" if a is None or b is None else f"{a-b:+.2f}"

princ = [r for r in rows if not r["consistencia_extra"]]
pend = [r for r in rows if r["nota_final_10"] is None]
L = ["# Relatório do Avaliador — Rodada 1 (reavaliação independente)", "",
     "Gerado por `scripts/avaliador.py` (rubrica), `scripts/avaliador_auditoria.py` (auditoria/reexecução) e `scripts/avaliador_relatorio.py`. "
     "As avaliações antigas (`avaliacao.json`, `RODADA.md`) não foram alteradas; as novas estão em `avaliacao_avaliador.json` em cada `run-N`. "
     "Aprovado pelo Lucas; `RODADA.md` foi regenerado a partir destas notas.", "",
     "## Metodologia", "",
     "- **Nota (0–10)** = 0,7 × (%testes/10) + 0,3 × rubrica(0–10). Mesma escala do `julgar.py`/`RODADA.md`. **Timeout = 0** (rubrica nem é julgada).",
     "- **Rubrica**: 5 itens de 0 a 2 do `rubrica.yaml` de cada tarefa; avalia o código entregue. Tipo 10: o item de documentação confere o `SUPOSICOES.md`. "
     "Tipo 08: o %testes é a taxa de mutantes mortos (os testes ocultos rodam a suíte do agente contra os mutantes plantados, 10–14 por tarefa).",
     "- **Juízes**: 2 por solução, média simples. Nenhum juiz é da empresa resolvedora nem da autora da tarefa (plano §6), então os 2 juízes são exatamente as 2 empresas restantes. "
     "Motores: Anthropic=`claude` (claude-haiku-5-5), OpenAI=`codex` (gpt-6-luna), Google=`agy` (gemini-3.8-flash), xAI=`grok` (grok-4.7-build-fast), todos esforço medium, os mesmos modelos de juiz do `julgar.py` para comparabilidade. "
     "Se um juiz falha 2 vezes, vale só o outro (registrado em `obs`).",
     "- **Anonimização**: código sem `enunciado.md`; nomes de modelo/empresa trocados por `[anon]`, linhas de autoria e caminhos absolutos removidos; juiz chamado fora da pasta, sem ferramentas de escrita.",
     "- **Escopo**: 16 combinações × 33 = 528 execuções (grok-4.7-high com regras excepcionais em 13 delas). A nota/ranking usa só as 30 execuções principais (run-1); as runs 2–4 da tarefa de consistência só medem variação. "
     "Obs.: o `RODADA.md` antigo usa N=33 (inclui as repetições) — por isso a comparação abaixo mostra também a nota antiga recalculada nas mesmas 30 execuções.",
     "- **grok-4.7-high**: 13 execuções refeitas seguem regra excepcional de tempo (1ª tentativa ≤300 s: nota cheia; 2ª tentativa de 900 s: máx. 70% — ≤600 s ×0,7, 600–900 s ×0,5, >900 s parcial ×0,5, sem entrega 0); detalhes na seção própria.",
     "- **Auditoria**: para cada execução, conferidos resultado.json × junit.xml × resumo do testes_saida.txt; caminho × campos; status × duração × timeout; arquivos de solução; "
     "hash dos testes_ocultos atuais × HEAD do git; mudanças não commitadas; histórico git do resultado.json; fórmula e juízes do avaliacao.json antigo; e **reexecução dos testes ocultos** sobre o código entregue (495/495).", ""]
if pend:
    L += [f"⚠️ {len(pend)} execuções sem nenhum juiz válido (nota pendente): " + ", ".join(r['pasta'] for r in pend), ""]

combos = sorted({r["combo"] for r in rows})
emp = {r["combo"]: r["empresa"] for r in rows}
tab = []
for c in combos:
    rs = [r for r in princ if r["combo"] == c]
    old33 = [r["nota_antiga_com_penalidade"] for r in rows if r["combo"] == c]
    tab.append(dict(c=c, e=emp[c], nova=m([r["nota_final_10"] for r in rs]), old30=m([r["nota_antiga_com_penalidade"] for r in rs]),
                    old33=m(old33), pct=m([r["pct_testes"] for r in rs]), rub=m([r["rubrica_media_10"] for r in rs]),
                    to=sum(r["status"] == "timeout" for r in rs), n=len(rs),
                    semp=m([round(0.7*r["pct_testes"]/10+0.3*r["rubrica_media_10"],2) if r.get("rubrica_media_10") is not None else None for r in rs])))
tab.sort(key=lambda t: -(t["nova"] or 0))
L += ["## Ranking novo por modelo × esforço (30 execuções principais)", "",
      "|#|Modelo|Empresa|Nota nova|Antiga (mesmas 30)|Δ|Antiga RODADA.md (33)|%testes|Rubrica nova (só não-timeout)|Timeouts|N|", "|-|-|-|-|-|-|-|-|-|-|-|"]
for i, t in enumerate(tab, 1):
    L.append(f"|{i}|{t['c']}|{t['e']}|**{fmt(t['nova'])}**|{fmt(t['old30'])}|{d(t['nova'], t['old30'])}|{fmt(t['old33'])}|{fmt(t['pct'])}|{fmt(t['rub'])}|{t['to']}|{t['n']}|")
L.append("")
L += ["## Ranking por empresa (média das combinações)", "", "|Empresa|Nota nova|Antiga (30)|Δ|", "|-|-|-|-|"]
for e in sorted({t["e"] for t in tab}, key=lambda e: -m([t["nova"] for t in tab if t["e"] == e])):
    n, o = m([t["nova"] for t in tab if t["e"] == e]), m([t["old30"] for t in tab if t["e"] == e])
    L.append(f"|{e}|{fmt(n)}|{fmt(o)}|{d(n,o)}|")
L.append("")
tipos = sorted({r["tipo"] for r in princ}); emps = sorted({r["empresa"] for r in princ})
L += ["## Tipo × empresa resolvedora (nota nova; antiga entre parênteses)", "", "|Tipo|" + "|".join(emps) + "|", "|-|" + "-|" * len(emps)]
for tp in tipos:
    cel = []
    for e in emps:
        rs = [r for r in princ if r["tipo"] == tp and r["empresa"] == e]
        cel.append(f"{fmt(m([r['nota_final_10'] for r in rs]))} ({fmt(m([r['nota_antiga_com_penalidade'] for r in rs]))})")
    L.append(f"|{tp}|" + "|".join(cel) + "|")
L += ["", "## Por tarefa (média das combinações que a resolveram)", "", "|Tarefa|N|Nota nova|Antiga|Δ|%testes|Timeouts|", "|-|-|-|-|-|-|-|"]
for tf in sorted({r["tarefa"] for r in princ}):
    rs = [r for r in princ if r["tarefa"] == tf]
    n, o = m([r["nota_final_10"] for r in rs]), m([r["nota_antiga_com_penalidade"] for r in rs])
    L.append(f"|{tf}|{len(rs)}|{fmt(n)}|{fmt(o)}|{d(n,o)}|{fmt(m([r['pct_testes'] for r in rs]))}|{sum(r['status']=='timeout' for r in rs)}|")
L += ["", "Matriz completa modelo × tarefa (nota antiga e nova por execução): `resultados/_avaliador/notas_avaliador.csv`.", ""]
# maiores diferenças
dif = sorted([r for r in princ if r["nota_final_10"] is not None], key=lambda r: -abs(r["nota_final_10"] - r["nota_antiga_com_penalidade"]))[:12]
L += ["### Maiores diferenças por execução", "", "|Execução|Antiga|Nova|Δ|Motivo provável|", "|-|-|-|-|-|"]
for r in dif:
    mot = "antiga sem juiz válido (rubrica 0)" if r["nota_antiga_avaliacao_json"] is None and r["status"] != "timeout" else ("reexecução dos testes" if r.get("nota_ajustada_por_reexecucao") else "rubrica")
    L.append(f"|{r['pasta'][11:]}|{fmt(r['nota_antiga_com_penalidade'])}|{fmt(r['nota_final_10'])}|{d(r['nota_final_10'], r['nota_antiga_com_penalidade'])}|{mot}|")
# consistência
L += ["", "## Consistência (tarefa fixa 04-dados-claude; Claude usa 04-dados-grok; runs 1–4) — não entra na nota", "",
      "|Modelo|Notas novas por run|Média|Desvio|Antiga média|", "|-|-|-|-|-|"]
for c in combos:
    rs = sorted([r for r in rows if r["combo"] == c and r["tarefa"] in ("04-dados-claude", "04-dados-grok") and
                 (emp[c] == "claude") == (r["tarefa"] == "04-dados-grok")], key=lambda r: r["run"])
    ns = [r["nota_final_10"] for r in rs if r["nota_final_10"] is not None]
    L.append(f"|{c}|{', '.join(fmt(x) for x in ns)}|{fmt(m(ns))}|{fmt(round(st.pstdev(ns),2) if len(ns)>1 else None)}|{fmt(m([r['nota_antiga_com_penalidade'] for r in rs]))}|")
# juízes
L += ["", "## Juízes", ""]
cnt = collections.Counter(); val = collections.defaultdict(list); diffs = []; um = 0
for r in rows:
    vs = []
    for j, v in r["juizes"].items():
        cnt[(j, "ok" if v["itens"] else "falhou")] += 1
        if v["rubrica_10"] is not None: val[j].append(v["rubrica_10"]); vs.append(v["rubrica_10"])
    if len(vs) == 2: diffs.append(abs(vs[0] - vs[1]))
    if len(vs) == 1: um += 1
julg = [r for r in rows if r["status"] != "timeout"]
L.append(f"- Execuções julgadas: {len(julg)} (timeouts não julgados: {len(rows)-len(julg)}). Com 2 juízes válidos: {len(diffs)}; com só 1: {um}; com 0: {len(pend)}.")
L.append(f"- |diferença| média entre juízes: {fmt(m(diffs))} pts; >3 pts: {sum(x>3 for x in diffs)}.")
for j in sorted(val):
    L.append(f"- {j}: média {fmt(m(val[j]))} (n={len(val[j])}), falhas definitivas {cnt[(j,'falhou')]}.")
# incoerências
L += ["", "## Incoerências encontradas", ""]
glob = ["**Pipeline/código:**",
        "- `runner/run.py` e `scripts/rodada.py` têm mudanças **não commitadas** (override `BENCH_TIMEOUT_S` até 900 s e campo `timeout_s` no resultado.json). As 495 execuções avaliadas aqui não têm `timeout_s` (geradas antes); só as refeitas do grok-4.7-high terão — o timeout delas não é o mesmo das demais.",
        "- `resultados/_timeouts_180s/` e `_timeouts_300s/` e `scripts/relatorio.py`, `site/` não estão versionados.",
        "- Plano §5 fala em 5 min padrão, mas todas as tarefas usam `timeout_min` do meta.yaml (ex.: 3 min em 04-dados-claude), o que explica boa parte dos timeouts do Gemini Flash e Grok high.",
        "- `RODADA.md` antigo: ranking com N=33 (inclui as 3 repetições de consistência, dando peso 4× à tarefa 04-dados) e execuções sem juiz válido entram com rubrica 0 (9 casos) em vez de ficarem pendentes.",
        "- `RODADA.md` antigo dizia que o mutation score do tipo 08 não foi calculado; na prática os testes ocultos do tipo 08 já são mutation testing com mutantes plantados — o %testes é a taxa de mortos. Corrigido no `RODADA.md` regenerado.",
        "- Harness `tarefas/08-testes-grok/testes_ocultos/test_mutantes.py`: no `except subprocess.TimeoutExpired` faz `(exc.stdout or \"\") + (exc.stderr or \"\")`, mas com `text=True` o `TimeoutExpired` traz bytes → `TypeError`. Sob carga (mutante >45 s) o teste falha por bug do harness, não do agente. **Corrigido** (só o tratamento do erro: decodifica bytes antes de concatenar; o que o teste avalia não mudou) e reexecutado nas 12 execuções da 08-testes-grok (grok não resolve tarefa própria): nenhuma contagem mudou em relação às notas do avaliador; a única afetada (gpt-6.1-sol-medium, 14/15 no resultado.json original) já usava 15/15 da reexecução. Detalhes em `resultados/_avaliador/rerun_08_testes_grok.json`.",
        "- Testes ocultos atuais: hash idêntico ao HEAD do git em todas as 40 tarefas; último commit em `tarefas/` (67ae40f, 29/10 19:05) é anterior ao início da rodada (19:07) — **nenhuma alteração de teste detectada**. Nenhum `codigo/` contém `testes_ocultos`.",
        "- Nenhum `resultado.json` diverge do `junit.xml` nem do resumo do `testes_saida.txt`; nenhuma `nota_final_10` antiga diverge da fórmula; nenhum juiz antigo não-neutro; nenhuma execução de tarefa da própria empresa. **Sem indício de edição manual de nota/resultado.**", "",
        "- **Arquivos não rastreados em resultados/ (pergunta do Bench - Grok)**: o avaliador **não criou nenhuma pasta de execução nova** (claude, codex ou outra). `git status --untracked-files=all` não mostra nenhuma pasta `run-N` nova fora do grok-4.7-high; os únicos arquivos não rastreados em `resultados/claude/` e `resultados/codex/` (e gemini/grok) são os `avaliacao_avaliador.json` criados por este avaliador, um por `run-N` — provavelmente o que foi visto. As reexecuções de testes rodam em cópias em /tmp e não gravam nada nas pastas.",
        "- grok-4.7-high: `04-dados-claude/run-2` e `run-3` aparecem como modificados (M) no git e os `avaliacao.json` antigos foram apagados (D) pela nova execução do Bench - Grok (versões antigas preservadas no HEAD do git e em `_erros_cota/`, `_timeouts_180s/`, `_timeouts_300s/`). As novas execuções têm `timeout_s` 300 ou 900, diferente dos 180 s/300 s da rodada original — assimetria de regras já conhecida.", "",
        "**Por execução:**", ""]
L += glob
porinc = collections.defaultdict(list)
for r in sorted(rows, key=lambda r: r["pasta"]):
    for i in r["incoerencias"]:
        porinc[i if "timeout com entrega" not in i else "TIMEOUT_PARCIAL"].append(r["pasta"][11:] + (f" ({i.split(': ')[1].split(',')[0]})" if "timeout com entrega" in i else ""))
for i, ps in porinc.items():
    if i == "TIMEOUT_PARCIAL":
        L.append(f"- {len(ps)} execuções com **timeout mas com entrega parcial que passa testes** (nota 0 pela regra; o grok-4.7-high terá regra diferente, o que cria assimetria): " + "; ".join(ps))
    else:
        L.append(f"- {i} — {len(ps)}: " + "; ".join(f"`{p}`" for p in ps))
L += ["", "## grok-4.7-high — regras excepcionais", "",
      "Regras excepcionais (decisão do Lucas), tempo pelo campo `duracao_agente_s` do agente, aplicadas sobre a nota normal (0,7×%testes + 0,3×rubrica):",
      "- 1ª tentativa (limite 300 s), concluída em até 300 s — 07-performance-claude, 06-multiarquivo-codex, 09-api-gemini: **nota cheia**.",
      "- 2ª tentativa (limite 900 s) — **teto de 70% mesmo se terminou em menos de 300 s**: até 600 s ×0,7; 600–900 s ×0,5; acima de 900 s com entrega parcial (avalia só o que está em `codigo/`) ×0,5; sem entrega (codigo/ igual ao inicial) = 0.",
      "- As outras 20 execuções do grok-4.7-high (rodada original/refeitas por cota) seguem a regra geral (timeout = 0).", "",
      "|Execução|Status|Duração (s)|%testes|Rubrica|Nota base|Regra|Nota final|", "|-|-|-|-|-|-|-|-|"]
for r in sorted([r for r in rows if r.get("regra_excepcional_grok_4_7_high")], key=lambda r: r["pasta"]):
    g = r["regra_excepcional_grok_4_7_high"]
    L.append(f"|{r['pasta'][len(GH):]}|{r['status']}|{r['duracao_agente_s']:.0f}|{r['pct_testes']:.0f}|{fmt(r.get('rubrica_media_10'))}|{fmt(g['nota_base'])}|{g['regra']}|**{fmt(r['nota_final_10'])}**|")
L.append("")
(RES / "RELATORIO_AVALIADOR.md").write_text("\n".join(L) + "\n")
with open(AV / "notas_avaliador.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["combo", "empresa", "tarefa", "run", "status", "pct_testes", "rubrica_nova", "nota_nova", "nota_antiga", "juizes", "incoerencias"])
    for r in sorted(rows, key=lambda r: r["pasta"]):
        w.writerow([r["combo"], r["empresa"], r["tarefa"], r["run"], r["status"], r["pct_testes"], r.get("rubrica_media_10"), r["nota_final_10"],
                    r["nota_antiga_com_penalidade"], "+".join(r["juizes"]), " | ".join(r["incoerencias"])])
print("ok", len(rows))

# ---------- RODADA.md regenerado ----------
R = ["# Rodada 1 — resultados (notas do avaliador)", "",
     "528 execuções (16 combinações × 33). Ranking com **N=30** por combinação (as 3 repetições de consistência ficam fora da nota). "
     "Nota final (0–10) = 0,7×%testes/10 + 0,3×rubrica (média de 2 juízes neutros: nenhum da empresa resolvedora nem da autora da tarefa; código anonimizado). **Timeout = 0.** "
     "Fonte: `avaliacao_avaliador.json` em cada execução; metodologia, auditoria e comparação com as notas antigas em `RELATORIO_AVALIADOR.md`.", "",
     "## Regras específicas", "",
     "- **Tipo 08 (testes)**: tem mutation score: os testes ocultos rodam a suíte escrita pelo agente contra mutantes plantados (10–14 por tarefa), e o %testes é a taxa de mutantes mortos. (A versão anterior deste arquivo dizia, por engano, que o mutation score não tinha sido calculado.)",
     "- **Correção no teste do tipo 08**: `tarefas/08-testes-grok/testes_ocultos/test_mutantes.py` concatenava texto com bytes no tratamento de timeout do mutante (`TypeError` sob carga). Corrigido só o tratamento do erro; o que o teste avalia não mudou. Reexecutado em todas as 12 execuções da 08-testes-grok: nenhuma nota do avaliador mudou (a gpt-6.1-sol-medium já contava 15/15 pela reexecução; o resultado.json original registrava 14/15).",
     "- **grok-4.7-high** (decisão do Lucas; tempo pelo campo `duracao_agente_s` do agente): 1ª tentativa concluída em até 300 s = nota cheia; 2ª tentativa (limite 900 s) = no máximo 70%: até 600 s ×0,7; de 600 a 900 s ×0,5; acima de 900 s com entrega parcial ×0,5; sem entrega, zero. As demais execuções dele seguem a regra geral.", "",
     "## Ranking modelo × esforço", "", "|#|Modelo|Nota|%testes|Rubrica (não-timeout)|Timeouts|N|", "|-|-|-|-|-|-|-|"]
for i, t in enumerate(tab, 1):
    R.append(f"|{i}|{t['c']} ({t['e']})|{fmt(t['nova'])}|{fmt(t['pct'])}|{fmt(t['rub'])}|{t['to']}|{t['n']}|")
R += ["", "## Por empresa", "", "|Empresa|Nota|", "|-|-|"]
for e in sorted({t["e"] for t in tab}, key=lambda e: -m([t["nova"] for t in tab if t["e"] == e])):
    R.append(f"|{e}|{fmt(m([t['nova'] for t in tab if t['e'] == e]))}|")
R += ["", "## Tipo × empresa", "", "|Tipo|" + "|".join(emps) + "|", "|-|" + "-|" * len(emps)]
for tp in tipos:
    R.append(f"|{tp}|" + "|".join(fmt(m([r['nota_final_10'] for r in princ if r['tipo'] == tp and r['empresa'] == e])) for e in emps) + "|")
R += ["", "## Medium vs high", "", "|Modelo|Medium|High|Δ|", "|-|-|-|-|"]
nt = {t["c"]: t["nova"] for t in tab}
for base in sorted({c.rsplit("-", 1)[0] for c in nt}):
    a, b = nt.get(base + "-medium"), nt.get(base + "-high")
    R.append(f"|{base}|{fmt(a)}|{fmt(b)}|{d(b, a)}|")
i0 = L.index(next(x for x in L if x.startswith("## Consistência")))
i1 = L.index("## Juízes")
R += [""] + L[i0:i1]
(RES / "RODADA.md").write_text("\n".join(R) + "\n")
print("RODADA.md ok")
