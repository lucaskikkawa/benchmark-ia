"""Auditoria (avaliador): confere resultado.json x junit.xml x testes_saida.txt x código, reexecuta os testes ocultos
e verifica alterações de teste/nota. Não altera arquivos antigos. Saída: resultados/_avaliador/auditoria.json
Uso: python scripts/avaliador_auditoria.py [--sem-rerun] [-j N]"""
import json, pathlib, re, subprocess, sys, tempfile, shutil, os, hashlib, datetime
from concurrent.futures import ThreadPoolExecutor
import yaml
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "runner"))
import run
ROOT = pathlib.Path(__file__).resolve().parent.parent
RES = ROOT / "resultados"
OUT = RES / "_avaliador"; OUT.mkdir(exist_ok=True)
PY = str(ROOT / ".bench-py" / "bin" / "python")

def alvos():
    for r in sorted(RES.glob("*/*/*/run-*/resultado.json")):
        rel = r.relative_to(RES).parts
        if rel[0].startswith("_") or rel[0] == "piloto" or (rel[1] == "grok-4.7-high") != ("--grok-high" in sys.argv):
            continue
        yield r.parent

def git(*a):
    return subprocess.run(["git", *a], cwd=ROOT, capture_output=True, text=True).stdout

def resumo_saida(txt):
    m = re.findall(r"^=*\s*(.*\b(?:passed|failed|error|errors)\b.*?) in [\d.]+s", txt, re.M)
    c = {"passed": 0, "failed": 0, "error": 0, "skipped": 0}
    if not m:
        return None
    for n, k in re.findall(r"(\d+) (passed|failed|errors?|skipped)", m[-1]):
        c["error" if k.startswith("error") else k] += int(n)
    return c

def hash_dir(d):
    h = hashlib.sha256()
    for p in sorted(d.rglob("*")):
        if p.is_file() and "__pycache__" not in p.parts:
            h.update(str(p.relative_to(d)).encode()); h.update(p.read_bytes())
    return h.hexdigest()[:16]

HASH_ORIG = {}
def hash_testes_head(tarefa):
    if tarefa not in HASH_ORIG:
        tmp = pathlib.Path(tempfile.mkdtemp())
        subprocess.run(f"git archive HEAD tarefas/{tarefa}/testes_ocultos | tar -x -C {tmp}", shell=True, cwd=ROOT)
        HASH_ORIG[tarefa] = (hash_dir(tmp / "tarefas" / tarefa / "testes_ocultos"), hash_dir(ROOT / "tarefas" / tarefa / "testes_ocultos"))
        shutil.rmtree(tmp)
    return HASH_ORIG[tarefa]

def rerun(rdir, tarefa):
    td = pathlib.Path(tempfile.mkdtemp(prefix="aval-"))
    try:
        run.copy_contents(rdir / "codigo", td)
        shutil.copytree(ROOT / "tarefas" / tarefa / "testes_ocultos", td / "testes_ocultos", dirs_exist_ok=True)
        cmd = ["unshare", "-rn", PY, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml=junit.xml", "testes_ocultos"]
        try:
            subprocess.run(cmd, cwd=td, capture_output=True, timeout=180)
        except subprocess.TimeoutExpired:
            return {"erro": "timeout 180s"}
        t, p, pct = run.parse_junit(td / "junit.xml")
        return {"total": t, "passados": p, "pct": round(pct, 2)}
    finally:
        shutil.rmtree(td, ignore_errors=True)

def auditar(rdir, fazer_rerun=True):
    inc = []
    rel = str(rdir.relative_to(ROOT))
    r = json.load(open(rdir / "resultado.json"))
    emp, combo, tarefa, runn = rdir.relative_to(RES).parts
    meta = yaml.safe_load(open(ROOT / "tarefas" / tarefa / "meta.yaml"))
    if (r["empresa"], f'{r["modelo"]}-{r["esforco"]}', r["tarefa"], f'run-{r["run"]}') != (emp, combo, tarefa, runn):
        inc.append(f"campos empresa/modelo/esforco/tarefa/run do resultado.json não batem com o caminho")
    if meta.get("autor") == emp:
        inc.append(f"tarefa autoral da própria empresa ({emp}) — viola a regra antiviés")
    # junit
    jt, jp, jpct = run.parse_junit(rdir / "junit.xml")
    if (jt, jp) != (r["testes_total"], r["testes_passados"]):
        inc.append(f"junit.xml diz {jp}/{jt}, resultado.json diz {r['testes_passados']}/{r['testes_total']}")
    if r["testes_total"] and abs(100 * r["testes_passados"] / r["testes_total"] - r["pct_passados"]) > 0.01:
        inc.append(f"pct_passados {r['pct_passados']} ≠ {r['testes_passados']}/{r['testes_total']}")
    # saída
    saida = (rdir / "testes_saida.txt").read_text(errors="replace") if (rdir / "testes_saida.txt").exists() else ""
    s = resumo_saida(saida)
    if s is None:
        if r["testes_total"]:
            inc.append("testes_saida.txt sem linha de resumo do pytest, mas resultado.json tem testes")
    else:
        if s["passed"] != r["testes_passados"] or sum(s.values()) != r["testes_total"]:
            inc.append(f"testes_saida.txt resume {s}, resultado.json diz {r['testes_passados']}/{r['testes_total']}")
    # tempo / status
    to = r.get("timeout_s") or min(300, int(meta.get("timeout_s") or 60 * float(meta.get("timeout_min", 5))))
    d = r.get("duracao_agente_s") or 0
    if "timeout_s" not in r:
        inc.append(f"resultado.json sem campo timeout_s (gerado antes da mudança não commitada do run.py); timeout inferido do meta = {to}s") if False else None
    if r["status"] == "ok" and d > to + 5:
        inc.append(f"status ok mas duração {d}s > timeout {to}s")
    if r["status"] == "timeout" and d < to - 5:
        inc.append(f"status timeout mas duração {d}s < timeout {to}s")
    if r["status"] == "ok" and r.get("exit_code") not in (0, None):
        inc.append(f"status ok com exit_code {r.get('exit_code')}")
    if r["status"] != "ok" and r["pct_passados"] > 0:
        inc.append(f"status {r['status']} mas {r['pct_passados']}% dos testes passaram (nota antiga zera; entrega parcial existe)") if False else None
    cod = [p for p in (rdir / "codigo").rglob("*") if p.is_file() and p.name != "enunciado.md" and "__pycache__" not in p.parts] if (rdir / "codigo").exists() else []
    for a in meta.get("arquivos_solucao") or []:
        if not (rdir / "codigo" / a).exists() and r["status"] == "ok":
            inc.append(f"status ok mas arquivo de solução esperado ausente: codigo/{a}")
    if (rdir / "codigo" / "testes_ocultos").exists():
        inc.append("codigo/ contém pasta testes_ocultos (agente não deveria ter acesso)")
    # mtimes
    try:
        ini = datetime.datetime.fromisoformat(r["inicio_iso"]).timestamp()
        mt = (rdir / "resultado.json").stat().st_mtime
        if mt < ini + d - 2:
            inc.append(f"resultado.json com mtime anterior ao fim da execução (inicio+duração)")
        if (rdir / "avaliacao.json").exists() and (rdir / "avaliacao.json").stat().st_mtime < mt - 1:
            inc.append("avaliacao.json mais antiga que resultado.json (resultado regravado após julgamento)")
    except Exception as e:
        inc.append(f"inicio_iso inválido: {e}")
    # testes alterados
    hh, hw = hash_testes_head(tarefa)
    if hh != hw:
        inc.append(f"tarefas/{tarefa}/testes_ocultos difere do HEAD do git")
    st = git("status", "--porcelain", "--", rel)
    if st.strip():
        inc.append(f"arquivos da execução com mudanças não commitadas: {st.strip().splitlines()[:5]}")
    nlog = len(git("log", "--format=%h", "--", f"{rel}/resultado.json").split())
    if nlog > 1:
        inc.append(f"resultado.json alterado em {nlog} commits: {git('log','--format=%h %s','--',f'{rel}/resultado.json').strip().splitlines()}")
    # avaliação antiga
    old = None
    if (rdir / "avaliacao.json").exists():
        old = json.load(open(rdir / "avaliacao.json"))
        rub = old.get("rubrica_10")
        if rub is not None:
            esperado = round(0.7 * r["pct_passados"] / 10 + 0.3 * rub, 2)
            if old.get("nota_final_10") is not None and abs(esperado - old["nota_final_10"]) > 0.011:
                inc.append(f"avaliacao.json nota_final_10 {old['nota_final_10']} ≠ fórmula {esperado}")
            vs = [j["rubrica_10"] for j in old.get("juizes", {}).values() if j.get("rubrica_10") is not None]
            if vs and abs(sum(vs) / len(vs) - rub) > 0.011:
                inc.append(f"avaliacao.json rubrica_10 {rub} ≠ média dos juízes {vs}")
            for jn, jv in old.get("juizes", {}).items():
                if jv.get("itens") and abs(sum(jv["itens"].values()) - (jv.get("rubrica_10") or 0)) > 0.01:
                    inc.append(f"juiz {jn}: soma dos itens ≠ rubrica_10")
        for jn in old.get("juizes", {}):
            if jn in (old.get("autora"), emp):
                inc.append(f"juiz antigo {jn} não é neutro (autora {old.get('autora')}, resolvedora {emp})")
        if old.get("autora") != meta.get("autor"):
            inc.append(f"avaliacao.json autora {old.get('autora')} ≠ meta.yaml {meta.get('autor')}")
    else:
        inc.append("sem avaliacao.json antiga")
    rr = rerun(rdir, tarefa) if fazer_rerun else None
    if rr and "erro" not in rr and (rr["total"], rr["passados"]) != (r["testes_total"], r["testes_passados"]):
        inc.append(f"reexecução dos testes deu {rr['passados']}/{rr['total']}, resultado.json diz {r['testes_passados']}/{r['testes_total']}")
    if rr and "erro" in rr:
        inc.append(f"reexecução: {rr['erro']}")
    return {"pasta": rel, "empresa": emp, "combo": combo, "tarefa": tarefa, "run": int(runn[4:]), "status": r["status"],
            "duracao_s": d, "timeout_s": to, "testes_total": r["testes_total"], "testes_passados": r["testes_passados"],
            "pct": r["pct_passados"], "rerun": rr, "nota_antiga": old.get("nota_final_10") if old else None,
            "rubrica_antiga": old.get("rubrica_10") if old else None, "n_arquivos_codigo": len(cod), "incoerencias": inc}

if __name__ == "__main__":
    j = int(sys.argv[sys.argv.index("-j") + 1]) if "-j" in sys.argv else 6
    lst = sys.argv[sys.argv.index("--lista") + 1] if "--lista" in sys.argv else None
    ds = [ROOT / x for x in open(lst).read().split()] if lst else list(alvos())
    for d in ds: hash_testes_head(d.parts[-2])
    with ThreadPoolExecutor(j) as ex:
        res = list(ex.map(lambda d: auditar(d, "--sem-rerun" not in sys.argv), ds))
    json.dump(res, open((pathlib.Path(sys.argv[sys.argv.index("--out") + 1]) if "--out" in sys.argv else OUT / ("auditoria_grok_high.json" if "--grok-high" in sys.argv else "auditoria.json")), "w"), ensure_ascii=False, indent=1)
    n = sum(1 for x in res if x["incoerencias"])
    print(len(res), "execuções;", n, "com incoerência")
