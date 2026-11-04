"""Cenário 'limite de 7 min': as 70 run-1 refeitas (timeout_s=420) substituem as originais; resto = oficial (notas_avaliador.csv).
Versão i: timeout = 0. Versão ii: timeout julgado como entrega normal. Saída em resultados/_avaliador/cenario_7min/."""
import csv, json, pathlib, statistics as st
ROOT = pathlib.Path(__file__).resolve().parent.parent; C = ROOT / "resultados/_avaliador/cenario_7min"
of = [r for r in csv.DictReader(open(ROOT / "resultados/_avaliador/notas_avaliador.csv")) if r["run"] == "1" and r["empresa"] != "grok"]
aud = {x["pasta"]: x for x in json.load(open(C / "auditoria_7min.json"))}
novos = {}
for p in (C / "execucoes_refeitas.txt").read_text().split():
    a = json.load(open(ROOT / p / "avaliacao_avaliador_7min.json"))
    base = round(0.7 * a["pct_testes"] / 10 + 0.3 * a["rubrica_media_10"], 2) if a.get("rubrica_media_10") is not None else None
    a["nota_i"] = 0.0 if a["status"] == "timeout" else base
    a["nota_ii"] = base
    a["incoerencias"] = aud.get(p, {}).get("incoerencias", [])
    a["reexecucao_testes"] = aud.get(p, {}).get("rerun")
    novos[(f'{a["modelo"]}-{a["esforco"]}', a["tarefa"])] = a
linhas = []
for r in of:
    k = (r["combo"], r["tarefa"]); n = novos.get(k)
    o = float(r["nota_nova"])
    linhas.append(dict(combo=r["combo"], empresa=r["empresa"], tarefa=r["tarefa"], status_oficial=r["status"], nota_oficial=o,
                       refeita=bool(n), status_7min=n["status"] if n else r["status"], duracao_7min=n["duracao_agente_s"] if n else None,
                       pct_7min=n["pct_testes"] if n else float(r["pct_testes"]), rubrica_7min=n.get("rubrica_media_10") if n else r["rubrica_nova"],
                       nota_i=n["nota_i"] if n else o, nota_ii=n["nota_ii"] if n else o))
faltam = set(novos) - {(l["combo"], l["tarefa"]) for l in linhas}
assert not faltam, faltam
with open(C / "notas_7min.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=list(linhas[0])); w.writeheader(); w.writerows(linhas)
json.dump(list(novos.values()), open(C / "notas_7min_refeitas.json", "w"), ensure_ascii=False, indent=1)
combos = sorted({l["combo"] for l in linhas})
def med(c, k): return st.mean(l[k] for l in linhas if l["combo"] == c)
res = {c: {k: med(c, k) for k in ("nota_oficial", "nota_i", "nota_ii")} for c in combos}
emp = {l["combo"]: l["empresa"] for l in linhas}
for c in combos: assert sum(l["combo"] == c for l in linhas) == 30, c
tarefas = sorted({l["tarefa"] for l in linhas})
with open(C / "matriz_7min.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["combo"] + [f"{t}|{v}" for t in tarefas for v in ("oficial", "i", "ii")])
    for c in combos:
        d = {l["tarefa"]: l for l in linhas if l["combo"] == c}
        w.writerow([c] + [x for t in tarefas for x in ((d[t]["nota_oficial"], d[t]["nota_i"], d[t]["nota_ii"]) if t in d else ("", "", ""))])
f2 = lambda x: f"{x:.2f}".replace(".", ",")
L = ["# Cenário “limite de 7 min” (420 s) — Claude, Codex e Gemini", "",
     "As 70 run-1 que deram timeout no oficial foram refeitas com 420 s. Neste cenário elas substituem as originais; o resto é igual ao oficial (`notas_avaliador.csv`), N=30 por combinação, sem Grok, sem consistência. "
     "Juízes: 2 neutros (≠ empresa resolvedora, ≠ autora da tarefa), código anonimizado, sem penalidade de atraso. "
     "**Versão i**: timeout = 0 (regra padrão). **Versão ii**: os timeouts de novo são julgados pelo que está em `codigo/` (%testes + rubrica).", "",
     "Arquivos: `notas_7min.csv` (360 execuções), `notas_7min_refeitas.json` (70), `matriz_7min.csv`, `auditoria_7min.json`; nas pastas run-N, `avaliacao_avaliador_7min.json`. Oficiais intocados.", ""]
for nome, k in (("(a) Ranking — oficial", "nota_oficial"), ("(a) Ranking — 7 min, versão i", "nota_i"), ("(a) Ranking — 7 min, versão ii", "nota_ii")):
    pass
L += ["## (a) Ranking das 12 combinações", "", "|Combinação|Oficial (#)|7 min i (#)|7 min ii (#)|Refeitas|Timeout de novo|", "|-|-|-|-|-|-|"]
pos = {k: {c: i + 1 for i, c in enumerate(sorted(combos, key=lambda c: -res[c][k]))} for k in ("nota_oficial", "nota_i", "nota_ii")}
for c in sorted(combos, key=lambda c: -res[c]["nota_i"]):
    nr = sum(1 for l in linhas if l["combo"] == c and l["refeita"]); nt = sum(1 for l in linhas if l["combo"] == c and l["refeita"] and l["status_7min"] == "timeout")
    L.append(f"|{c}|{f2(res[c]['nota_oficial'])} ({pos['nota_oficial'][c]})|{f2(res[c]['nota_i'])} ({pos['nota_i'][c]})|{f2(res[c]['nota_ii'])} ({pos['nota_ii'][c]})|{nr}|{nt}|")
L += ["", "## (b) Médias por empresa (média das 4 combinações)", "", "|Empresa|Oficial|7 min i|7 min ii|", "|-|-|-|-|"]
for e in ("claude", "codex", "gemini"):
    cs = [c for c in combos if emp[c] == e]
    L.append(f"|{e}|" + "|".join(f2(st.mean(res[c][k] for c in cs)) for k in ("nota_oficial", "nota_i", "nota_ii")) + "|")
pares = {"haiku": "claude-haiku-5-5", "opus": "claude-opus-5-5", "luna": "gpt-6-luna", "sol": "gpt-6.1-sol", "argon": "gemini-4-argon", "flash": "gemini-3.8-flash"}
L += ["", "## (c) high − medium por par", "", "|Par|Oficial|7 min i|7 min ii|", "|-|-|-|-|"]
hm = {}
for p, b in pares.items():
    hm[p] = {k: res[b + "-high"][k] - res[b + "-medium"][k] for k in ("nota_oficial", "nota_i", "nota_ii")}
    L.append(f"|{p}|" + "|".join(f"{hm[p][k]:+.2f}".replace(".", ",") for k in ("nota_oficial", "nota_i", "nota_ii")) + "|")
L += ["", "## Execuções refeitas", "", "|Combinação|Tarefa|Status 7 min|Duração (s)|%testes|Rubrica|Nota oficial|Nota i|Nota ii|", "|-|-|-|-|-|-|-|-|-|"]
for l in sorted([l for l in linhas if l["refeita"]], key=lambda l: (l["combo"], l["tarefa"])):
    L.append(f"|{l['combo']}|{l['tarefa']}|{l['status_7min']}|{l['duracao_7min']:.0f}|{l['pct_7min']:.0f}|{'—' if l['rubrica_7min'] is None else f2(l['rubrica_7min'])}|{f2(l['nota_oficial'])}|{f2(l['nota_i'])}|{f2(l['nota_ii'])}|")
L += ["", "## Incoerências", ""]
inc = [(p, i) for p, x in aud.items() for i in x["incoerencias"] if "avaliacao_avaliador" not in i]
L += [f"- `{p}`: {i}" for p, i in inc] or ["- Nenhuma na auditoria das 70 (resultado.json × junit.xml × testes_saida.txt × reexecução)."]
L.append("__EXTRA__")
(C / "RELATORIO_7MIN.md").write_text("\n".join(L) + "\n")
json.dump({"res": res, "hm": hm, "pos": pos, "inc": inc}, open(C / "resumo_7min.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({"hm": hm}, indent=0)); [print(c, {k: round(v, 2) for k, v in res[c].items()}) for c in combos]; print(len(inc), "incoerências")
