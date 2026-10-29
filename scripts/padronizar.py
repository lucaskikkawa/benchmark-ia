import yaml, pathlib, sys
for t in sorted(pathlib.Path("tarefas").glob("[0-9]*-*")):
    r = yaml.safe_load((t/"rubrica.yaml").read_text())
    src = r["itens"] if isinstance(r, dict) and "itens" in r else [dict(v, id=k) for k, v in r.items() if isinstance(v, dict)]
    out = []
    for it in src:
        niv = it.get("niveis") or it.get("descricao") if isinstance(it.get("descricao"), dict) else it.get("niveis")
        niv = {int(k): v for k, v in (niv or {}).items()}
        crit = it.get("criterio") or (it["descricao"] if isinstance(it.get("descricao"), str) else it["id"].replace("_", " "))
        out.append({"id": it["id"], "criterio": crit, 0: niv.get(0, it.get(0)), 1: niv.get(1, it.get(1)), 2: niv.get(2, it.get(2))})
    assert len(out) == 5 and all(o[k] for o in out for k in (0,1,2)), (t, out)
    (t/"rubrica.yaml").write_text(yaml.safe_dump({"itens": out}, allow_unicode=True, sort_keys=False, width=1000))
    m = yaml.safe_load((t/"meta.yaml").read_text())
    if "timeout_s" in m: m["timeout_min"] = max(1, round(m.pop("timeout_s")/60))
    m["timeout_min"] = min(int(m.get("timeout_min", 3)), 5)
    m["comando_teste"] = m.get("comando_teste") or "python -m pytest -q testes_ocultos"
    (t/"meta.yaml").write_text(yaml.safe_dump(m, allow_unicode=True, sort_keys=False, width=1000))
print("ok")
