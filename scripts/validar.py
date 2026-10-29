#!/usr/bin/env python3
"""Valida tarefas: referencia passa 100%; inicial falha (02/03); estrutura ok."""
import shutil, subprocess, sys, tempfile, pathlib, yaml, json
ROOT = pathlib.Path(__file__).resolve().parent.parent / "tarefas"
def run(t, with_ref):
    d = pathlib.Path(tempfile.mkdtemp())
    for sub in (["inicial", "referencia"] if with_ref else ["inicial"]):
        s = t / sub
        if s.exists(): shutil.copytree(s, d, dirs_exist_ok=True)
    shutil.copytree(t / "testes_ocultos", d / "testes_ocultos")
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "testes_ocultos"], cwd=d, capture_output=True, text=True, timeout=300)
    shutil.rmtree(d, ignore_errors=True)
    return r.returncode, r.stdout.strip().splitlines()[-1] if r.stdout.strip() else r.stderr[-200:]
res = {}
for t in sorted(p for p in ROOT.iterdir() if p.is_dir() and not p.name.startswith("_")):
    if len(sys.argv) > 1 and not any(a in t.name for a in sys.argv[1:]): continue
    e = []
    for f in ["enunciado.md", "rubrica.yaml", "meta.yaml", "testes_ocultos", "referencia"]:
        if not (t / f).exists(): e.append("falta " + f)
    try:
        rb = yaml.safe_load((t/"rubrica.yaml").read_text()); m = yaml.safe_load((t/"meta.yaml").read_text())
    except Exception as x: e.append(f"yaml: {x}"); m = {}
    rc, s = run(t, True)
    if rc: e.append("REF FALHA: " + s)
    out = {"ref": s}
    if t.name[:2] in ("02", "03"):
        rc2, s2 = run(t, False); out["inicial"] = s2
        if rc2 == 0: e.append("inicial passa (deveria falhar)")
    out["erros"] = e; res[t.name] = out
    print(("OK  " if not e else "ERR ") + t.name, out)
json.dump(res, open(ROOT.parent / "notas" / "validacao.json", "w"), indent=1, ensure_ascii=False)
