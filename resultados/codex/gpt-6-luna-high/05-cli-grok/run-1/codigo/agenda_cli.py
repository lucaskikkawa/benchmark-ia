#!/usr/bin/env python3
"""CLI simples para manter uma agenda pessoal em JSON."""

import argparse
import datetime
import json
import os
import re
import sys


PRIORIDADES = ("baixa", "media", "alta")
ORDEM_PRIORIDADE = {"alta": 0, "media": 1, "baixa": 2}
CHAVES_ARQUIVO = {"proximo_id", "tarefas"}
CHAVES_TAREFA = {"id", "titulo", "prioridade", "prazo", "concluida"}
PADRAO_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")


def erro(mensagem):
    print(f"erro: {mensagem}", file=sys.stderr)
    raise SystemExit(2)


def inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def data_valida(valor):
    if not isinstance(valor, str) or not PADRAO_DATA.fullmatch(valor):
        return False
    try:
        datetime.date.fromisoformat(valor)
    except ValueError:
        return False
    return True


def pares_sem_duplicatas(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError("chave duplicada")
        objeto[chave] = valor
    return objeto


def tarefa_valida(tarefa):
    if not isinstance(tarefa, dict) or set(tarefa) != CHAVES_TAREFA:
        return False
    if not inteiro(tarefa["id"]) or tarefa["id"] < 1:
        return False
    titulo = tarefa["titulo"]
    if not isinstance(titulo, str) or not titulo or titulo.strip() != titulo:
        return False
    if any(caractere in titulo for caractere in "\n\r\t"):
        return False
    # Surrogates isolados não podem ser gravados como UTF-8 pelo formato definido.
    if any(0xD800 <= ord(caractere) <= 0xDFFF for caractere in titulo):
        return False
    if tarefa["prioridade"] not in PRIORIDADES:
        return False
    if tarefa["prazo"] is not None and not data_valida(tarefa["prazo"]):
        return False
    if not isinstance(tarefa["concluida"], bool):
        return False
    return True


def carregar(caminho):
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            dados = json.load(arquivo, object_pairs_hook=pares_sem_duplicatas)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError):
        erro("arquivo invalido")

    if not isinstance(dados, dict) or set(dados) != CHAVES_ARQUIVO:
        erro("arquivo invalido")
    proximo_id = dados["proximo_id"]
    tarefas = dados["tarefas"]
    if not inteiro(proximo_id) or proximo_id < 1 or not isinstance(tarefas, list):
        erro("arquivo invalido")
    ids = set()
    for tarefa in tarefas:
        if not tarefa_valida(tarefa) or tarefa["id"] in ids:
            erro("arquivo invalido")
        ids.add(tarefa["id"])
    if ids and proximo_id <= max(ids):
        erro("arquivo invalido")
    return dados


def gravar(caminho, dados):
    conteudo = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
    try:
        with open(caminho, "w", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(conteudo)
    except (OSError, UnicodeError):
        erro("arquivo invalido")


def adicionar(args):
    titulo = args.titulo.strip()
    if not titulo:
        erro("titulo vazio")
    if any(caractere in titulo for caractere in "\n\r\t"):
        erro("titulo invalido")
    if not os.path.exists(args.arquivo):
        dados = {"proximo_id": 1, "tarefas": []}
    else:
        dados = carregar(args.arquivo)
    novo_id = dados["proximo_id"]
    dados["tarefas"].append({
        "id": novo_id,
        "titulo": titulo,
        "prioridade": args.prioridade,
        "prazo": args.prazo,
        "concluida": False,
    })
    dados["proximo_id"] = novo_id + 1
    gravar(args.arquivo, dados)
    print(f"ok id={novo_id}")


def listar(args):
    if not os.path.exists(args.arquivo):
        erro("arquivo inexistente")
    dados = carregar(args.arquivo)
    tarefas = dados["tarefas"]
    if args.prioridade is not None:
        tarefas = [t for t in tarefas if t["prioridade"] == args.prioridade]
    if args.somente_abertas:
        tarefas = [t for t in tarefas if not t["concluida"]]
    tarefas = sorted(tarefas, key=lambda t: (ORDEM_PRIORIDADE[t["prioridade"]], t["id"]))
    for tarefa in tarefas:
        estado = "concluida" if tarefa["concluida"] else "aberta"
        prazo = tarefa["prazo"] if tarefa["prazo"] is not None else "-"
        print(f"{tarefa['id']}\t{tarefa['prioridade']}\t{estado}\t{prazo}\t{tarefa['titulo']}")


def concluir(args):
    if not os.path.exists(args.arquivo):
        erro("arquivo inexistente")
    dados = carregar(args.arquivo)
    tarefa = next((t for t in dados["tarefas"] if t["id"] == args.id), None)
    if tarefa is None:
        erro("id inexistente")
    if tarefa["concluida"]:
        erro("ja concluida")
    tarefa["concluida"] = True
    gravar(args.arquivo, dados)
    print(f"ok id={args.id}")


def criar_parser():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="comando", required=True)

    parser_adicionar = subparsers.add_parser("adicionar")
    parser_adicionar.add_argument("--titulo", required=True)
    parser_adicionar.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    parser_adicionar.add_argument("--prazo", type=str)
    parser_adicionar.add_argument("--arquivo", required=True)
    parser_adicionar.set_defaults(func=adicionar)

    parser_listar = subparsers.add_parser("listar")
    parser_listar.add_argument("--arquivo", required=True)
    parser_listar.add_argument("--prioridade", choices=PRIORIDADES)
    parser_listar.add_argument("--somente-abertas", action="store_true")
    parser_listar.set_defaults(func=listar)

    parser_concluir = subparsers.add_parser("concluir")
    parser_concluir.add_argument("--id", required=True, type=int)
    parser_concluir.add_argument("--arquivo", required=True)
    parser_concluir.set_defaults(func=concluir)
    return parser


def main():
    parser = criar_parser()
    args = parser.parse_args()
    if args.comando == "adicionar" and args.prazo is not None and not data_valida(args.prazo):
        erro("prazo invalido")
    args.func(args)


if __name__ == "__main__":
    main()
