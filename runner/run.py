#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import signal
import shlex
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PROMPT = "Leia enunciado.md neste diretório e resolva a tarefa editando/criando arquivos aqui. Não pergunte nada; trabalhe só neste diretório."
IGNORED = {"__pycache__", ".git", ".pytest_cache"}


def copy_contents(src, dst):
    def ignore(_directory, names):
        return [name for name in names if name in IGNORED]

    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, ignore=ignore, dirs_exist_ok=True)
        else:
            shutil.copy2(item, target)


HOME = os.path.expanduser("~")
RO_SYS = ["/usr", "/bin", "/sbin", "/lib", "/lib64", "/etc", "/opt", "/run", "/node_modules"]
RO_HOME = [".local", ".profile", ".bashrc", ".gitconfig", "cli-config"]
RW_HOME = [".codex", ".claude", ".claude.json", ".grok", ".gemini", ".cache", ".npm", ".config/gh"]


def bwrap(cmd, wd):
    """Agente vê só a pasta da execução (rw), binários (ro) e configs das CLIs."""
    b = ["bwrap", "--die-with-parent", "--unshare-pid", "--proc", "/proc", "--dev", "/dev",
         "--tmpfs", "/tmp", "--tmpfs", "/home", "--dir", HOME]
    for d in RO_SYS:
        if os.path.exists(d):
            b += ["--ro-bind", d, d]
    for d in RO_HOME:
        x = os.path.join(HOME, d)
        if os.path.exists(x):
            b += ["--ro-bind", x, x]
    for d in RW_HOME:
        x = os.path.join(HOME, d)
        if os.path.exists(x):
            b += ["--bind", x, x]
    b += ["--bind", str(wd), str(wd), "--chdir", str(wd), "--setenv", "HOME", HOME, "--"]
    return b + cmd


def command_for(empresa, modelo, esforco, wd):
    return bwrap(_agent_cmd(empresa, modelo, esforco, wd), wd)


def _agent_cmd(empresa, modelo, esforco, wd):
    if empresa == "codex":
        return ["codex", "exec", "--skip-git-repo-check", "--dangerously-bypass-approvals-and-sandbox",
                "-C", str(wd), "-m", modelo, "-c", f"model_reasoning_effort={esforco}", PROMPT]
    if empresa == "claude":
        return ["claude", "-p", PROMPT, "--dangerously-skip-permissions", "--model", modelo, "--effort", esforco]
    if empresa == "gemini":
        return ["agy", "-p", PROMPT, "--model", f"{modelo}-{esforco}", "--dangerously-skip-permissions"]
    return ["grok", "-p", PROMPT, "-m", modelo, "--effort", esforco,
            "--permission-mode", "bypassPermissions", "--cwd", str(wd)]


def run_process(cmd, cwd, timeout, merge=False):
    proc = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT if merge else subprocess.PIPE,
                            start_new_session=True)
    try:
        out, err = proc.communicate(timeout=timeout)
        return proc.returncode, out.decode(errors="replace"), ("" if merge else err.decode(errors="replace")), False
    except subprocess.TimeoutExpired:
        try:
            os.killpg(proc.pid, signal.SIGKILL)
        except ProcessLookupError:
            pass
        out, err = proc.communicate()
        return proc.returncode, out.decode(errors="replace"), ("" if merge else err.decode(errors="replace")), True


def parse_junit(path):
    try:
        root = ET.parse(path).getroot()
        def number(key):
            if key in root.attrib:
                return int(root.attrib[key])
            return sum(int(node.attrib.get(key, 0)) for node in root.iter("testsuite"))
        total, failures, errors, skipped = (number(k) for k in ("tests", "failures", "errors", "skipped"))
        passed = max(0, total - failures - errors - skipped)
        return total, passed, (100.0 * passed / total if total else 0.0)
    except (ET.ParseError, OSError, ValueError):
        return 0, 0, 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--empresa", required=True, choices=("codex", "claude", "gemini", "grok"))
    parser.add_argument("--modelo", required=True)
    parser.add_argument("--esforco", required=True, choices=("medium", "high"))
    parser.add_argument("--tarefa", required=True)
    parser.add_argument("--run", type=int)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    task = ROOT / "tarefas" / args.tarefa
    enunciado = task / "enunciado.md"
    if not enunciado.is_file():
        parser.error(f"arquivo não encontrado: {enunciado}")
    meta = {}
    if (task / "meta.yaml").exists():
        import yaml
        with (task / "meta.yaml").open(encoding="utf-8") as f:
            meta = yaml.safe_load(f) or {}
    timeout_s = min(300, max(1, int(meta.get("timeout_s", 300))))

    base = ROOT / "resultados" / args.empresa / f"{args.modelo}-{args.esforco}" / args.tarefa
    if args.run is None:
        run_n = 1
        while (base / f"run-{run_n}").exists():
            run_n += 1
    else:
        run_n = args.run
        if run_n < 1:
            parser.error("--run deve ser maior que zero")
    output = base / f"run-{run_n}"
    workdir = Path(tempfile.mkdtemp(prefix="bench-"))
    testdir = None
    try:
        shutil.copy2(enunciado, workdir / "enunciado.md")
        initial = task / "inicial"
        if initial.is_dir():
            copy_contents(initial, workdir)
        cmd = command_for(args.empresa, args.modelo, args.esforco, workdir)
        if args.dry_run:
            print(json.dumps(cmd, ensure_ascii=False))
            return

        start = datetime.now(timezone.utc).astimezone().isoformat()
        began = time.monotonic()
        status, exit_code = "ok", None
        try:
            exit_code, agent_out, agent_err, timed_out = run_process(cmd, workdir, timeout_s)
            if timed_out:
                status = "timeout"
            elif exit_code != 0:
                status = "erro"
        except Exception as exc:
            agent_out, agent_err = "", f"{type(exc).__name__}: {exc}\n"
            status = "erro"
        duration = round(time.monotonic() - began, 3)

        output.mkdir(parents=True, exist_ok=True)
        (output / "agente_stdout.txt").write_text(agent_out, encoding="utf-8")
        (output / "agente_stderr.txt").write_text(agent_err, encoding="utf-8")
        copy_contents(workdir, output / "codigo")

        testdir = Path(tempfile.mkdtemp(prefix="bench-"))
        copy_contents(workdir, testdir)
        hidden = task / "testes_ocultos"
        if hidden.is_dir():
            shutil.copytree(hidden, testdir / "testes_ocultos", dirs_exist_ok=True)
        py = os.environ.get("BENCH_PY", str(ROOT / ".bench-py" / "bin" / "python"))
        configured_test = shlex.split(str(meta.get("cmd_teste", "pytest -q testes_ocultos")))
        if configured_test == ["pytest", "-q", "testes_ocultos"]:
            test_cmd = ["unshare", "-rn", py, "-m", "pytest", "-q", "-p", "no:cacheprovider",
                        "--junitxml=junit.xml", "testes_ocultos"]
        elif configured_test and Path(configured_test[0]).name == "pytest":
            test_args = configured_test[1:]
            test_cmd = ["unshare", "-rn", py, "-m", "pytest", *test_args]
            if not any(arg.startswith("--junitxml") for arg in test_args):
                test_cmd.append("--junitxml=junit.xml")
            if "-p" not in test_args and "--disable-warnings" not in test_args:
                test_cmd.extend(["-p", "no:cacheprovider"])
        else:
            test_cmd = ["unshare", "-rn", *configured_test]
        try:
            test_code, test_out, test_err, test_timeout = run_process(test_cmd, testdir, 120, merge=True)
            tests_output = test_out + ("\n[timeout]\n" if test_timeout else "")
        except Exception as exc:
            tests_output = f"{type(exc).__name__}: {exc}\n"
        (output / "testes_saida.txt").write_text(tests_output, encoding="utf-8")
        junit = testdir / "junit.xml"
        if junit.exists():
            shutil.copy2(junit, output / "junit.xml")
        else:
            (output / "junit.xml").write_text("", encoding="utf-8")
        total, passed, pct = parse_junit(junit)
        result = {"empresa": args.empresa, "modelo": args.modelo, "esforco": args.esforco,
                  "tarefa": args.tarefa, "run": run_n, "status": status, "exit_code": exit_code,
                  "duracao_agente_s": duration, "testes_total": total, "testes_passados": passed,
                  "pct_passados": pct, "inicio_iso": start, "cmd": cmd}
        (output / "resultado.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(result, ensure_ascii=False, indent=2))
    finally:
        shutil.rmtree(workdir, ignore_errors=True)
        if testdir:
            shutil.rmtree(testdir, ignore_errors=True)


if __name__ == "__main__":
    main()
