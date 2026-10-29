"""Juiz da rubrica: empresa que não é autora nem resolvedora, código anonimizado."""
import json, os, re, subprocess, sys, tempfile, pathlib, yaml
sys.path.insert(0, "runner"); import run
JUIZ = {"claude": ("grok", "grok-4.7-build-fast"), "gemini": ("claude", "claude-haiku-5-5"),
        "grok": ("gemini", "gemini-3.8-flash")}
CODEX_JUIZ = {"gpt-6-luna": (os.environ.get("JE","gemini"), os.environ.get("JM","gemini-3.8-flash")), "gpt-6.1-sol": ("grok", "grok-4.7-build-fast")}

def julgar(rdir):
    r = json.load(open(rdir / "resultado.json"))
    tarefa = pathlib.Path("tarefas") / r["tarefa"]
    je, jm = CODEX_JUIZ[r["modelo"]] if r["empresa"] == "codex" else JUIZ[r["empresa"]]
    meta = yaml.safe_load(open(tarefa / "meta.yaml"))
    codigo = ""
    for p in sorted((rdir / "codigo").rglob("*.py")):
        if "__pycache__" not in p.parts:
            src = re.sub(r"(?im)^\s*#.*\b(claude|gpt|codex|gemini|grok|anthropic|openai|xai)\b.*$", "", p.read_text())
            codigo += f"\n### {p.relative_to(rdir/'codigo')}\n```python\n{src}\n```\n"
    prompt = (f"Você é avaliador de código. Enunciado:\n{(tarefa/'enunciado.md').read_text()}\n"
              f"Rubrica (cada item 0-2):\n{(tarefa/'rubrica.yaml').read_text()}\nSolução anônima:{codigo}\n"
              "Não use ferramentas. Responda APENAS um JSON: {\"<item>\": nota, ...} com os 5 itens.")
    wd = tempfile.mkdtemp(prefix="juiz-")
    pf = pathlib.Path(wd, "p.txt"); pf.write_text(prompt)
    run.PROMPT = "Leia o arquivo p.txt neste diretório e siga as instruções dele. Responda só com o JSON pedido."
    cmd = run.command_for(je, jm, "medium", wd)
    out = subprocess.run(cmd, cwd=wd, capture_output=True, text=True, timeout=300).stdout
    m = re.findall(r"\{[^{}]*\}", out)
    notas = json.loads(m[-1]) if m else {}
    rub = sum(min(2, max(0, float(v))) for v in notas.values()) if len(notas) == 5 else None
    pct = r["pct_passados"]
    final = round(0.7 * pct / 10 + 0.3 * rub, 2) if rub is not None else None
    res = {"juiz_empresa": je, "juiz_modelo": jm, "itens": notas, "rubrica_10": rub, "nota_final_10": final}
    if rub is None: res["saida_bruta"] = out[-2000:]
    json.dump(res, open(rdir / "avaliacao.json", "w"), ensure_ascii=False, indent=1)
    print(r["empresa"], r["modelo"], r["esforco"], je, rub, final, flush=True)

if __name__ == "__main__":
    for d in sys.argv[1:]: julgar(pathlib.Path(d))
