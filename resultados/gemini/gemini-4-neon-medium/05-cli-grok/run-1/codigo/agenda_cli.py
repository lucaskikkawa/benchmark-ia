#!/usr/bin/env python3
"""CLI de agenda pessoal."""

import argparse
import datetime
import json
import os
import re
import sys
from typing import Any

PRIORIDADES = ("baixa", "media", "alta")
ORDEM_PRIORIDADE = {"alta": 0, "media": 1, "baixa": 2}
CHAVES_RAIZ = {"proximo_id", "tarefas"}
CHAVES_TAREFA = {"id", "titulo", "prioridade", "prazo", "concluida"}
REGEX_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


class ErroRegra(Exception):
    """Erro de regra de negócio que deve encerrar com código 2."""


def validar_data(valor: Any) -> bool:
    if not isinstance(valor, str) or not REGEX_DATA.fullmatch(valor):
        return False
    ano = int(valor[0:4])
    mes = int(valor[5:7])
    dia = int(valor[8:10])
    try:
        datetime.date(ano, mes, dia)
    except ValueError:
        return False
    return True


def validar_titulo_json(valor: Any) -> bool:
    if not isinstance(valor, str):
        return False
    if not valor or valor != valor.strip():
        return False
    if any(ch in valor for ch in ("\n", "\r", "\t")):
        return False
    return True


def _sem_chaves_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in obj:
            raise ValueError("chave duplicada")
        obj[chave] = valor
    return obj


def _rejeitar_constante(_valor: str) -> Any:
    raise ValueError("constante JSON invalida")


def validar_estrutura(dados: Any) -> dict[str, Any]:
    if not isinstance(dados, dict) or set(dados.keys()) != CHAVES_RAIZ:
        raise ErroRegra("arquivo invalido")

    proximo_id = dados["proximo_id"]
    if type(proximo_id) is not int or proximo_id < 1:
        raise ErroRegra("arquivo invalido")

    tarefas = dados["tarefas"]
    if not isinstance(tarefas, list):
        raise ErroRegra("arquivo invalido")

    ids_vistos: set[int] = set()
    for tarefa in tarefas:
        if not isinstance(tarefa, dict) or set(tarefa.keys()) != CHAVES_TAREFA:
            raise ErroRegra("arquivo invalido")

        tid = tarefa["id"]
        if type(tid) is not int or tid < 1 or tid in ids_vistos or tid >= proximo_id:
            raise ErroRegra("arquivo invalido")
        ids_vistos.add(tid)

        if not validar_titulo_json(tarefa["titulo"]):
            raise ErroRegra("arquivo invalido")

        prioridade = tarefa["prioridade"]
        if not isinstance(prioridade, str) or prioridade not in PRIORIDADES:
            raise ErroRegra("arquivo invalido")

        prazo = tarefa["prazo"]
        if prazo is not None and not validar_data(prazo):
            raise ErroRegra("arquivo invalido")

        if type(tarefa["concluida"]) is not bool:
            raise ErroRegra("arquivo invalido")

    return dados


def carregar_arquivo(caminho: str, criar_se_ausente: bool) -> dict[str, Any]:
    if not os.path.exists(caminho):
        if criar_se_ausente:
            return {"proximo_id": 1, "tarefas": []}
        raise ErroRegra("arquivo inexistente")

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
        dados = json.loads(
            conteudo,
            object_pairs_hook=_sem_chaves_duplicadas,
            parse_constant=_rejeitar_constante,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        raise ErroRegra("arquivo invalido") from None

    return validar_estrutura(dados)


def salvar_arquivo(caminho: str, dados: dict[str, Any]) -> None:
    texto = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def cmd_adicionar(args: argparse.Namespace) -> None:
    titulo = args.titulo.strip()
    if not titulo:
        raise ErroRegra("titulo vazio")
    if any(ch in titulo for ch in ("\n", "\r", "\t")):
        raise ErroRegra("titulo invalido")

    prazo = args.prazo
    if prazo is not None and not validar_data(prazo):
        raise ErroRegra("prazo invalido")

    dados = carregar_arquivo(args.arquivo, criar_se_ausente=True)
    novo_id = dados["proximo_id"]
    dados["tarefas"].append(
        {
            "id": novo_id,
            "titulo": titulo,
            "prioridade": args.prioridade,
            "prazo": prazo,
            "concluida": False,
        }
    )
    dados["proximo_id"] = novo_id + 1
    salvar_arquivo(args.arquivo, dados)
    sys.stdout.write(f"ok id={novo_id}\n")


def cmd_listar(args: argparse.Namespace) -> None:
    dados = carregar_arquivo(args.arquivo, criar_se_ausente=False)
    tarefas = dados["tarefas"]

    if args.prioridade is not None:
        tarefas = [t for t in tarefas if t["prioridade"] == args.prioridade]
    if args.somente_abertas:
        tarefas = [t for t in tarefas if not t["concluida"]]

    tarefas_ordenadas = sorted(
        tarefas, key=lambda t: (ORDEM_PRIORIDADE[t["prioridade"]], t["id"])
    )

    for t in tarefas_ordenadas:
        estado = "concluida" if t["concluida"] else "aberta"
        prazo = t["prazo"] if t["prazo"] is not None else "-"
        sys.stdout.write(
            f"{t['id']}\t{t['prioridade']}\t{estado}\t{prazo}\t{t['titulo']}\n"
        )


def cmd_concluir(args: argparse.Namespace) -> None:
    dados = carregar_arquivo(args.arquivo, criar_se_ausente=False)

    alvo = None
    for tarefa in dados["tarefas"]:
        if tarefa["id"] == args.id:
            alvo = tarefa
            break

    if alvo is None:
        raise ErroRegra("id inexistente")
    if alvo["concluida"]:
        raise ErroRegra("ja concluida")

    alvo["concluida"] = True
    salvar_arquivo(args.arquivo, dados)
    sys.stdout.write(f"ok id={alvo['id']}\n")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agenda_cli.py")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_add = subparsers.add_parser("adicionar")
    p_add.add_argument("--titulo", required=True)
    p_add.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    p_add.add_argument("--prazo", default=None)
    p_add.add_argument("--arquivo", required=True)
    p_add.set_defaults(func=cmd_adicionar)

    p_list = subparsers.add_parser("listar")
    p_list.add_argument("--arquivo", required=True)
    p_list.add_argument("--prioridade", default=None, choices=PRIORIDADES)
    p_list.add_argument("--somente-abertas", action="store_true")
    p_list.set_defaults(func=cmd_listar)

    p_done = subparsers.add_parser("concluir")
    p_done.add_argument("--id", required=True, type=int)
    p_done.add_argument("--arquivo", required=True)
    p_done.set_defaults(func=cmd_concluir)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = construir_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ErroRegra as exc:
        sys.stderr.write(f"erro: {exc}\n")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
