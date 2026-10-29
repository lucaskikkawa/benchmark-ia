"""Rodada completa: 4 empresas em paralelo, 2 execuções simultâneas por empresa, retomável.

Uso: python scripts/rodada.py [--empresas codex,claude,...] [--tarefas 01-funcao-codex,...] [--sem-consistencia] [--dry-run]
Pula execuções que já têm resultado.json. Log de progresso em resultados/rodada.log.
"""
import argparse, json, pathlib, subprocess, sys, threading, time, queue
from concurrent.futures import ThreadPoolExecutor
import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
PY = str(ROOT / ".bench-py" / "bin" / "python")
MODELOS = {  # ordem importa: no Gemini, o Flash vem antes do Argon (cota)
    "codex": ["gpt-6-luna", "gpt-6.1-sol"],
    "claude": ["claude-haiku-5-5", "claude-opus-5-5"],
    "gemini": ["gemini-3.8-flash", "gemini-4-argon"],
    "grok": ["grok-4.7-build-fast", "grok-4.7"],
}
ESFORCOS = ["medium", "high"]
CONSIST = {"default": "04-dados-claude", "claude": "04-dados-grok"}  # tarefas/SELECAO.md
REPETICOES = 3  # execuções extras (run-2..run-4) da tarefa de consistência
LOG = ROOT / "resultados" / "rodada.log"
lock = threading.Lock()


def log(msg):
    linha = f"{time.strftime('%H:%M:%S')} {msg}"
    with lock:
        print(linha, flush=True)
        with open(LOG, "a") as f:
            f.write(linha + "\n")


def tarefas_de(empresa, filtro):
    out = []
    for d in sorted((ROOT / "tarefas").iterdir()):
        if not d.is_dir() or d.name.startswith("_") or not (d / "meta.yaml").exists():
            continue
        if yaml.safe_load(open(d / "meta.yaml")).get("autor") == empresa:
            continue
        if filtro and d.name not in filtro:
            continue
        out.append(d.name)
    return out


def jobs_de(empresa, filtro, consistencia):
    jobs = []
    cons = CONSIST.get(empresa, CONSIST["default"])
    for m in MODELOS[empresa]:
        for e in ESFORCOS:
            ts = tarefas_de(empresa, filtro)
            for t in ts:
                jobs.append((empresa, m, e, t, 1))
            if consistencia and cons in ts:
                for n in range(2, 2 + REPETICOES):
                    jobs.append((empresa, m, e, cons, n))
    return jobs


def feito(job):
    empresa, m, e, t, n = job
    return (ROOT / "resultados" / empresa / f"{m}-{e}" / t / f"run-{n}" / "resultado.json").exists()


def executar(job, dry):
    empresa, m, e, t, n = job
    if feito(job):
        log(f"PULA  {empresa} {m}-{e} {t} run-{n} (já tem resultado)")
        return
    log(f"INICIO {empresa} {m}-{e} {t} run-{n}")
    if dry:
        return
    t0 = time.time()
    p = subprocess.run([PY, "runner/run.py", "--empresa", empresa, "--modelo", m, "--esforco", e,
                        "--tarefa", t, "--run", str(n)], cwd=ROOT, capture_output=True, text=True)
    try:
        r = json.loads(p.stdout[p.stdout.index("{"):])
        info = f"status={r['status']} testes={r['testes_passados']}/{r['testes_total']} agente={r['duracao_agente_s']:.0f}s"
    except Exception:
        info = f"ERRO runner exit={p.returncode} {p.stderr.strip()[-300:]}"
    log(f"FIM   {empresa} {m}-{e} {t} run-{n} {info} total={time.time() - t0:.0f}s")


def empresa_worker(empresa, jobs, dry, paralelo):
    pend = [j for j in jobs if not feito(j)]
    log(f"EMPRESA {empresa}: {len(jobs)} execuções, {len(pend)} pendentes")
    with ThreadPoolExecutor(max_workers=paralelo) as ex:  # a fila respeita a ordem (Flash antes do Argon)
        list(ex.map(lambda j: executar(j, dry), jobs))
    log(f"EMPRESA {empresa}: concluída")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--empresas", default="codex,claude,gemini,grok")
    ap.add_argument("--tarefas", default="")
    ap.add_argument("--paralelo", type=int, default=2)
    ap.add_argument("--sem-consistencia", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    LOG.parent.mkdir(exist_ok=True)
    filtro = set(filter(None, a.tarefas.split(",")))
    emps = a.empresas.split(",")
    log(f"=== rodada: empresas={emps} paralelo={a.paralelo} dry={a.dry_run}")
    ths = [threading.Thread(target=empresa_worker,
                            args=(e, jobs_de(e, filtro, not a.sem_consistencia), a.dry_run, a.paralelo)) for e in emps]
    t0 = time.time()
    for t in ths: t.start()
    for t in ths: t.join()
    log(f"=== rodada concluída em {(time.time() - t0) / 60:.1f} min")


if __name__ == "__main__":
    main()
