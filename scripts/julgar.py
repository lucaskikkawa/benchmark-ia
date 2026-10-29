"""Rubrica com 2 juízes neutros (nem a autora da tarefa nem a resolvedora), com o código anonimizado.

Uso: python scripts/julgar.py <pasta run-N> [...]   (pula se avaliacao.json já existe, salvo --refazer)
"""
import json, pathlib, re, subprocess, sys, tempfile, shutil, os, signal
import yaml
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "runner"))
import run

ROOT = pathlib.Path(__file__).resolve().parent.parent
BARATOS = {"codex": "gpt-6-luna", "claude": "claude-haiku-5-5",
           "gemini": "gemini-3.8-flash", "grok": "grok-4.7-build-fast"}
TIMEOUT = 120
MARCAS = r"claude|gpt|codex|gemini|grok|anthropic|openai|xai|antigravity"


def itens_rubrica(rub):
    """Aceita o formato padronizado (itens: lista) e o antigo (chaves soltas)."""
    if isinstance(rub.get("itens"), list):
        return [i["id"] for i in rub["itens"]]
    return [k for k, v in rub.items() if isinstance(v, dict) and "max" in v]


def anonimizar(rdir):
    codigo = ""
    for p in sorted((rdir / "codigo").rglob("*")):
        if not p.is_file() or "__pycache__" in p.parts or p.name == "enunciado.md":
            continue
        if p.suffix not in (".py", ".md", ".txt", ".toml", ".yaml", ".yml", ".json", ".cfg"):
            continue
        src = p.read_text(errors="replace")
        src = re.sub(rf"(?im)^.*\b({MARCAS})\b.*(gerad|written|feito|created|author).*$", "", src)
        codigo += f"\n### {p.relative_to(rdir / 'codigo')}\n```\n{src[:20000]}\n```\n"
    return codigo


def chamar_juiz(empresa, prompt):
    wd = tempfile.mkdtemp(prefix="juiz-")
    try:
        pathlib.Path(wd, "p.txt").write_text(prompt)
        run.PROMPT = "Leia o arquivo p.txt neste diretório e siga as instruções dele. Responda só com o JSON pedido."
        cmd = run.command_for(empresa, BARATOS[empresa], "medium", wd)
        proc = subprocess.Popen(cmd, cwd=wd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                                text=True, start_new_session=True)
        try:
            out, _ = proc.communicate(timeout=TIMEOUT)
        except subprocess.TimeoutExpired:
            os.killpg(proc.pid, signal.SIGKILL); proc.communicate()
            return None, "timeout"
        return out, None
    finally:
        shutil.rmtree(wd, ignore_errors=True)


def nota_de(out, ids):
    for m in reversed(re.findall(r"\{[^{}]*\}", out or "")):
        try:
            d = json.loads(m)
        except ValueError:
            continue
        if all(i in d for i in ids):
            return {i: min(2.0, max(0.0, float(d[i]))) for i in ids}
    return None


def julgar(rdir, refazer=False):
    if (rdir / "avaliacao.json").exists() and not refazer:
        return
    r = json.load(open(rdir / "resultado.json"))
    tarefa = ROOT / "tarefas" / r["tarefa"]
    autora = yaml.safe_load(open(tarefa / "meta.yaml")).get("autor")
    rub_txt = (tarefa / "rubrica.yaml").read_text()
    ids = itens_rubrica(yaml.safe_load(rub_txt))
    juizes = [e for e in BARATOS if e not in (autora, r["empresa"])][:2]
    prompt = (f"Você é avaliador de código. Enunciado da tarefa:\n{(tarefa / 'enunciado.md').read_text()}\n"
              f"Rubrica (cada item vale de 0 a 2):\n{rub_txt}\nSolução anônima:{anonimizar(rdir)}\n"
              f"Não use ferramentas nem rode nada. Responda APENAS um JSON numa linha com as chaves {ids} e notas 0, 1 ou 2.")
    av = {"autora": autora, "resolvedora": r["empresa"], "juizes": {}, "obs": []}
    for j in juizes:
        res = None
        for tentativa in (1, 2):
            out, erro = chamar_juiz(j, prompt)
            res = nota_de(out, ids)
            if res:
                break
            av["obs"].append(f"{j} tentativa {tentativa} falhou: {erro or 'JSON inválido'}")
        av["juizes"][j] = {"modelo": BARATOS[j], "itens": res, "rubrica_10": sum(res.values()) if res else None}
    validas = [v["rubrica_10"] for v in av["juizes"].values() if v["rubrica_10"] is not None]
    if len(validas) == 1:
        av["obs"].append("só 1 juiz válido; usada só a nota dele")
    av["rubrica_10"] = round(sum(validas) / len(validas), 2) if validas else None
    av["nota_final_10"] = (round(0.7 * r["pct_passados"] / 10 + 0.3 * av["rubrica_10"], 2)
                           if av["rubrica_10"] is not None else None)
    json.dump(av, open(rdir / "avaliacao.json", "w"), ensure_ascii=False, indent=1)
    print(r["empresa"], r["modelo"], r["esforco"], r["tarefa"], rdir.name, av["rubrica_10"], av["nota_final_10"], av["obs"], flush=True)


if __name__ == "__main__":
    refazer = "--refazer" in sys.argv
    for d in [a for a in sys.argv[1:] if a != "--refazer"]:
        julgar(pathlib.Path(d), refazer)
