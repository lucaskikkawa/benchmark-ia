#!/usr/bin/env python3
"""CLI simples para manter uma agenda de tarefas em JSON."""

import argparse
import datetime
import json
import os
import re
import sys


PRIORIDADES = ("baixa", "media", "alta")
CHAVES_RAIZ = {"proximo_id", "tarefas"}
CHAVES_TAREFA = {"id", "titulo", "prioridade", "prazo", "concluida"}


class ErroRegra(Exception):
    pass


def inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def data_valida(valor):
    if not isinstance(valor, str) or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", valor) is None:
        return False
    try:
        datetime.date.fromisoformat(valor)
    except ValueError:
        return False
    return True


def arquivo_valido(dados):
    if not isinstance(dados, dict) or set(dados) != CHAVES_RAIZ:
        return False
    proximo = dados["proximo_id"]
    tarefas = dados["tarefas"]
    if not inteiro(proximo) or proximo < 1 or not isinstance(tarefas, list):
        return False
    ids = set()
    for tarefa in tarefas:
        if not isinstance(tarefa, dict) or set(tarefa) != CHAVES_TAREFA:
            return False
        ident = tarefa["id"]
        titulo = tarefa["titulo"]
        prioridade = tarefa["prioridade"]
        prazo = tarefa["prazo"]
        concluida = tarefa["concluida"]
        if not inteiro(ident) or ident < 1 or ident in ids:
            return False
        ids.add(ident)
        if (not isinstance(titulo, str) or not titulo or titulo != titulo.strip()
                or any(c in titulo for c in "\n\r\t")):
            return False
        if prioridade not in PRIORIDADES:
            return False
        if prazo is not None and not data_valida(prazo):
            return False
        if not isinstance(concluida, bool):
            return False
    return proximo > max(ids, default=0)


def carregar(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo)
    except (OSError, UnicodeError, json.JSONDecodeError):
        raise ErroRegra("arquivo invalido")
    if not arquivo_valido(dados):
        raise ErroRegra("arquivo invalido")
    return dados


def salvar(caminho, dados):
    with open(caminho, "w", encoding="utf-8", newline="\n") as arquivo:
        json.dump(dados, arquivo, ensure_ascii=False, indent=2)
        arquivo.write("\n")


def prazo_cli(valor):
    if not data_valida(valor):
        raise ErroRegra("prazo invalido")
    return valor


def criar_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="comando", required=True)

    adicionar = subparsers.add_parser("adicionar")
    adicionar.add_argument("--titulo", required=True)
    adicionar.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    adicionar.add_argument("--prazo", type=prazo_cli)
    adicionar.add_argument("--arquivo", required=True)

    listar = subparsers.add_parser("listar")
    listar.add_argument("--arquivo", required=True)
    listar.add_argument("--prioridade", choices=PRIORIDADES)
    listar.add_argument("--somente-abertas", action="store_true")

    concluir = subparsers.add_parser("concluir")
    concluir.add_argument("--id", required=True, type=int)
    concluir.add_argument("--arquivo", required=True)
    return parser


def executar(args):
    if args.comando == "adicionar":
        titulo = args.titulo.strip()
        if not titulo:
            raise ErroRegra("titulo vazio")
        if any(c in titulo for c in "\n\r\t"):
            raise ErroRegra("titulo invalido")
        if os.path.exists(args.arquivo):
            dados = carregar(args.arquivo)
        else:
            dados = {"proximo_id": 1, "tarefas": []}
        ident = dados["proximo_id"]
        dados["tarefas"].append({
            "id": ident,
            "titulo": titulo,
            "prioridade": args.prioridade,
            "prazo": args.prazo,
            "concluida": False,
        })
        dados["proximo_id"] = ident + 1
        try:
            salvar(args.arquivo, dados)
        except OSError:
            raise ErroRegra("arquivo invalido")
        print(f"ok id={ident}")
        return

    if not os.path.exists(args.arquivo):
        raise ErroRegra("arquivo inexistente")
    dados = carregar(args.arquivo)

    if args.comando == "listar":
        ordem = {"alta": 0, "media": 1, "baixa": 2}
        tarefas = sorted(dados["tarefas"], key=lambda t: (ordem[t["prioridade"]], t["id"]))
        for tarefa in tarefas:
            if args.prioridade is not None and tarefa["prioridade"] != args.prioridade:
                continue
            if args.somente_abertas and tarefa["concluida"]:
                continue
            estado = "concluida" if tarefa["concluida"] else "aberta"
            prazo = tarefa["prazo"] if tarefa["prazo"] is not None else "-"
            print(f"{tarefa['id']}\t{tarefa['prioridade']}\t{estado}\t{prazo}\t{tarefa['titulo']}")
        return

    tarefa = next((t for t in dados["tarefas"] if t["id"] == args.id), None)
    if tarefa is None:
        raise ErroRegra("id inexistente")
    if tarefa["concluida"]:
        raise ErroRegra("ja concluida")
    tarefa["concluida"] = True
    try:
        salvar(args.arquivo, dados)
    except OSError:
        raise ErroRegra("arquivo invalido")
    print(f"ok id={args.id}")


def main():
    parser = criar_parser()
    try:
        args = parser.parse_args()
        executar(args)
    except ErroRegra as erro:
        sys.stdout.write("")
        sys.stderr.write(f"erro: {erro}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
