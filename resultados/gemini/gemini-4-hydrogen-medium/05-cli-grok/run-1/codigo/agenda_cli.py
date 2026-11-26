#!/usr/bin/env python3
import argparse
import datetime
import json
import re
import sys
from pathlib import Path
from typing import Any

PRIORIDADES = ("baixa", "media", "alta")
PRIORIDADE_ORDEM = {"alta": 0, "media": 1, "baixa": 2}
DATE_RE = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
INVALID_TITLE_CHARS = ("\n", "\r", "\t")
ROOT_KEYS = {"proximo_id", "tarefas"}
TASK_KEYS = {"id", "titulo", "prioridade", "prazo", "concluida"}


class RuleError(Exception):
    """Erro de regra de negocio que encerra o programa com codigo 2."""


def is_strict_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def is_valid_date(value: str) -> bool:
    if DATE_RE.fullmatch(value) is None:
        return False
    year, month, day = map(int, value.split("-"))
    try:
        datetime.date(year, month, day)
        return True
    except ValueError:
        return False


def validate_title_value(title: str) -> bool:
    if not title:
        return False
    if title != title.strip():
        return False
    if any(ch in title for ch in INVALID_TITLE_CHARS):
        return False
    return True


def reject_json_constant(_value: str) -> None:
    raise ValueError("Invalid JSON constant")


def validate_agenda_data(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict) or set(data.keys()) != ROOT_KEYS:
        raise RuleError("arquivo invalido")

    proximo_id = data["proximo_id"]
    tarefas = data["tarefas"]

    if not is_strict_int(proximo_id) or proximo_id < 1:
        raise RuleError("arquivo invalido")
    if not isinstance(tarefas, list):
        raise RuleError("arquivo invalido")

    seen_ids: set[int] = set()
    for task in tarefas:
        if not isinstance(task, dict) or set(task.keys()) != TASK_KEYS:
            raise RuleError("arquivo invalido")

        tid = task["id"]
        if not is_strict_int(tid) or tid < 1 or tid in seen_ids or tid >= proximo_id:
            raise RuleError("arquivo invalido")
        seen_ids.add(tid)

        titulo = task["titulo"]
        if not isinstance(titulo, str) or not validate_title_value(titulo):
            raise RuleError("arquivo invalido")

        prioridade = task["prioridade"]
        if not isinstance(prioridade, str) or prioridade not in PRIORIDADES:
            raise RuleError("arquivo invalido")

        prazo = task["prazo"]
        if prazo is not None and (not isinstance(prazo, str) or not is_valid_date(prazo)):
            raise RuleError("arquivo invalido")

        concluida = task["concluida"]
        if not isinstance(concluida, bool):
            raise RuleError("arquivo invalido")

    return data


def load_agenda(path: Path, allow_missing: bool) -> dict[str, Any]:
    if not path.exists():
        if allow_missing:
            return {"proximo_id": 1, "tarefas": []}
        raise RuleError("arquivo inexistente")

    try:
        raw = path.read_text(encoding="utf-8")
        data = json.loads(raw, parse_constant=reject_json_constant)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError, RecursionError) as exc:
        raise RuleError("arquivo invalido") from exc

    return validate_agenda_data(data)


def save_agenda(path: Path, data: dict[str, Any]) -> None:
    serialized = json.dumps(data, indent=2, ensure_ascii=False) + "\n"
    path.write_text(serialized, encoding="utf-8")


def handle_adicionar(args: argparse.Namespace) -> int:
    titulo = args.titulo.strip()
    if not titulo:
        raise RuleError("titulo vazio")
    if any(ch in titulo for ch in INVALID_TITLE_CHARS):
        raise RuleError("titulo invalido")

    prazo = args.prazo
    if prazo is not None and not is_valid_date(prazo):
        raise RuleError("prazo invalido")

    path = Path(args.arquivo)
    data = load_agenda(path, allow_missing=True)

    novo_id = data["proximo_id"]
    data["proximo_id"] = novo_id + 1
    data["tarefas"].append(
        {
            "id": novo_id,
            "titulo": titulo,
            "prioridade": args.prioridade,
            "prazo": prazo,
            "concluida": False,
        }
    )
    save_agenda(path, data)
    sys.stdout.write(f"ok id={novo_id}\n")
    return 0


def handle_listar(args: argparse.Namespace) -> int:
    path = Path(args.arquivo)
    data = load_agenda(path, allow_missing=False)

    tarefas = data["tarefas"]
    if args.prioridade is not None:
        tarefas = [t for t in tarefas if t["prioridade"] == args.prioridade]
    if args.somente_abertas:
        tarefas = [t for t in tarefas if not t["concluida"]]

    tarefas_ordenadas = sorted(
        tarefas,
        key=lambda t: (PRIORIDADE_ORDEM[t["prioridade"]], t["id"]),
    )

    lines = [
        f"{t['id']}\t{t['prioridade']}\t{'concluida' if t['concluida'] else 'aberta'}\t"
        f"{t['prazo'] if t['prazo'] is not None else '-'}\t{t['titulo']}\n"
        for t in tarefas_ordenadas
    ]
    if lines:
        sys.stdout.write("".join(lines))
    return 0


def handle_concluir(args: argparse.Namespace) -> int:
    path = Path(args.arquivo)
    data = load_agenda(path, allow_missing=False)

    alvo = None
    for tarefa in data["tarefas"]:
        if tarefa["id"] == args.id:
            alvo = tarefa
            break

    if alvo is None:
        raise RuleError("id inexistente")
    if alvo["concluida"]:
        raise RuleError("ja concluida")

    alvo["concluida"] = True
    save_agenda(path, data)
    sys.stdout.write(f"ok id={args.id}\n")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agenda_cli.py")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_add = subparsers.add_parser("adicionar")
    p_add.add_argument("--titulo", required=True)
    p_add.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    p_add.add_argument("--prazo", default=None)
    p_add.add_argument("--arquivo", required=True)
    p_add.set_defaults(func=handle_adicionar)

    p_list = subparsers.add_parser("listar")
    p_list.add_argument("--arquivo", required=True)
    p_list.add_argument("--prioridade", default=None, choices=PRIORIDADES)
    p_list.add_argument("--somente-abertas", action="store_true")
    p_list.set_defaults(func=handle_listar)

    p_done = subparsers.add_parser("concluir")
    p_done.add_argument("--id", required=True, type=int)
    p_done.add_argument("--arquivo", required=True)
    p_done.set_defaults(func=handle_concluir)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except RuleError as exc:
        sys.stderr.write(f"erro: {exc}\n")
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
