#!/usr/bin/env python3
import argparse
import datetime
import json
import os
import re
import sys


class ErroRegra(Exception):
    pass


DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}\Z")


def validate_date(d: str) -> bool:
    if not isinstance(d, str) or not DATE_RE.match(d):
        return False
    try:
        y = int(d[0:4])
        m = int(d[5:7])
        day = int(d[8:10])
        if y < 1 or y > 9999:
            return False
        datetime.date(y, m, day)
        return True
    except (ValueError, OverflowError):
        return False


def check_duplicate_keys(pairs):
    keys = set()
    d = {}
    for k, v in pairs:
        if k in keys:
            raise ValueError(f"chave duplicada: {k}")
        keys.add(k)
        d[k] = v
    return d


def carregar_e_validar_arquivo(caminho: str) -> dict:
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            content = f.read()
        data = json.loads(content, object_pairs_hook=check_duplicate_keys)
    except Exception:
        raise ErroRegra("arquivo invalido")

    if not isinstance(data, dict):
        raise ErroRegra("arquivo invalido")

    if set(data.keys()) != {"proximo_id", "tarefas"}:
        raise ErroRegra("arquivo invalido")

    proximo_id = data["proximo_id"]
    if type(proximo_id) is not int or proximo_id < 1:
        raise ErroRegra("arquivo invalido")

    tarefas = data["tarefas"]
    if type(tarefas) is not list:
        raise ErroRegra("arquivo invalido")

    seen_ids = set()
    for t in tarefas:
        if not isinstance(t, dict):
            raise ErroRegra("arquivo invalido")

        if set(t.keys()) != {"id", "titulo", "prioridade", "prazo", "concluida"}:
            raise ErroRegra("arquivo invalido")

        t_id = t["id"]
        if type(t_id) is not int or t_id < 1:
            raise ErroRegra("arquivo invalido")
        if t_id in seen_ids:
            raise ErroRegra("arquivo invalido")
        seen_ids.add(t_id)

        titulo = t["titulo"]
        if type(titulo) is not str:
            raise ErroRegra("arquivo invalido")
        if len(titulo) == 0:
            raise ErroRegra("arquivo invalido")
        if titulo != titulo.strip():
            raise ErroRegra("arquivo invalido")
        if any(c in titulo for c in ("\n", "\r", "\t")):
            raise ErroRegra("arquivo invalido")

        prioridade = t["prioridade"]
        if type(prioridade) is not str or prioridade not in ("baixa", "media", "alta"):
            raise ErroRegra("arquivo invalido")

        prazo = t["prazo"]
        if prazo is not None:
            if type(prazo) is not str or not validate_date(prazo):
                raise ErroRegra("arquivo invalido")

        concluida = t["concluida"]
        if type(concluida) is not bool:
            raise ErroRegra("arquivo invalido")

    if any(proximo_id <= t_id for t_id in seen_ids):
        raise ErroRegra("arquivo invalido")

    return data


def salvar_arquivo(caminho: str, data: dict) -> None:
    parent = os.path.dirname(caminho)
    if parent and not os.path.exists(parent):
        os.makedirs(parent, exist_ok=True)
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def cmd_adicionar(args) -> None:
    # 1. Validar titulo
    titulo = args.titulo.strip()
    if not titulo:
        raise ErroRegra("titulo vazio")
    if any(c in args.titulo for c in ("\n", "\r", "\t")):
        raise ErroRegra("titulo invalido")

    # 2. Validar prazo
    if args.prazo is not None:
        if not validate_date(args.prazo):
            raise ErroRegra("prazo invalido")

    # 3. Arquivo
    caminho = args.arquivo
    if not os.path.exists(caminho):
        data = {"proximo_id": 1, "tarefas": []}
    else:
        data = carregar_e_validar_arquivo(caminho)

    novo_id = data["proximo_id"]
    data["proximo_id"] += 1
    nova_tarefa = {
        "id": novo_id,
        "titulo": titulo,
        "prioridade": args.prioridade,
        "prazo": args.prazo,
        "concluida": False,
    }
    data["tarefas"].append(nova_tarefa)

    salvar_arquivo(caminho, data)
    sys.stdout.write(f"ok id={novo_id}\n")


def cmd_listar(args) -> None:
    caminho = args.arquivo
    if not os.path.exists(caminho):
        raise ErroRegra("arquivo inexistente")

    data = carregar_e_validar_arquivo(caminho)
    tarefas = data["tarefas"]

    # Filtros
    if args.prioridade is not None:
        tarefas = [t for t in tarefas if t["prioridade"] == args.prioridade]

    if args.somente_abertas:
        tarefas = [t for t in tarefas if not t["concluida"]]

    # Ordem: prioridade alta, depois media, depois baixa; id crescente
    prio_order = {"alta": 0, "media": 1, "baixa": 2}
    tarefas.sort(key=lambda t: (prio_order[t["prioridade"]], t["id"]))

    for t in tarefas:
        estado = "concluida" if t["concluida"] else "aberta"
        prazo = t["prazo"] if t["prazo"] is not None else "-"
        sys.stdout.write(f"{t['id']}\t{t['prioridade']}\t{estado}\t{prazo}\t{t['titulo']}\n")


def cmd_concluir(args) -> None:
    caminho = args.arquivo
    if not os.path.exists(caminho):
        raise ErroRegra("arquivo inexistente")

    data = carregar_e_validar_arquivo(caminho)

    target_task = None
    for t in data["tarefas"]:
        if t["id"] == args.id:
            target_task = t
            break

    if target_task is None:
        raise ErroRegra("id inexistente")

    if target_task["concluida"]:
        raise ErroRegra("ja concluida")

    target_task["concluida"] = True
    salvar_arquivo(caminho, data)
    sys.stdout.write(f"ok id={args.id}\n")


def main() -> None:
    parser = argparse.ArgumentParser(prog="agenda_cli.py")
    subparsers = parser.add_subparsers(dest="subcomando", required=True)

    # adicionar
    p_add = subparsers.add_parser("adicionar")
    p_add.add_argument("--titulo", required=True)
    p_add.add_argument("--prioridade", choices=["baixa", "media", "alta"], required=True)
    p_add.add_argument("--prazo", default=None)
    p_add.add_argument("--arquivo", required=True)

    # listar
    p_list = subparsers.add_parser("listar")
    p_list.add_argument("--arquivo", required=True)
    p_list.add_argument("--prioridade", choices=["baixa", "media", "alta"], default=None)
    p_list.add_argument("--somente-abertas", action="store_true")

    # concluir
    p_done = subparsers.add_parser("concluir")
    p_done.add_argument("--id", type=int, required=True)
    p_done.add_argument("--arquivo", required=True)

    args = parser.parse_args()

    try:
        if args.subcomando == "adicionar":
            cmd_adicionar(args)
        elif args.subcomando == "listar":
            cmd_listar(args)
        elif args.subcomando == "concluir":
            cmd_concluir(args)
    except ErroRegra as e:
        sys.stderr.write(f"erro: {e}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
