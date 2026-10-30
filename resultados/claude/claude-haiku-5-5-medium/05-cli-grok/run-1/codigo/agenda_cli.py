#!/usr/bin/env python3
"""Agenda pessoal em linha de comando, com arquivo JSON."""

import argparse
import datetime
import json
import os
import re
import sys

PRIORIDADES = ("baixa", "media", "alta")
ORDEM_PRIORIDADE = {"alta": 0, "media": 1, "baixa": 2}
CHAVES_RAIZ = {"proximo_id", "tarefas"}
CHAVES_TAREFA = {"id", "titulo", "prioridade", "prazo", "concluida"}
PADRAO_PRAZO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
CARACTERES_PROIBIDOS = ("\n", "\r", "\t")


class ErroAgenda(Exception):
    """Erro de regra: vira `erro: MENSAGEM` no stderr, com código 2."""


def escrever_saida(texto):
    sys.stdout.buffer.write(texto.encode("utf-8"))
    sys.stdout.buffer.flush()


def escrever_erro(mensagem):
    sys.stderr.buffer.write(f"erro: {mensagem}\n".encode("utf-8"))
    sys.stderr.buffer.flush()


def data_valida(texto):
    if not PADRAO_PRAZO.fullmatch(texto):
        return False
    ano, mes, dia = (int(parte) for parte in texto.split("-"))
    try:
        datetime.date(ano, mes, dia)
    except ValueError:
        return False
    return True


def objeto_sem_duplicatas(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(f"chave duplicada: {chave}")
        objeto[chave] = valor
    return objeto


def validar_tarefa(tarefa):
    if not isinstance(tarefa, dict) or set(tarefa) != CHAVES_TAREFA:
        raise ErroAgenda("arquivo invalido")
    if type(tarefa["id"]) is not int or tarefa["id"] < 1:
        raise ErroAgenda("arquivo invalido")
    titulo = tarefa["titulo"]
    if (
        not isinstance(titulo, str)
        or not titulo
        or titulo != titulo.strip()
        or any(caractere in titulo for caractere in CARACTERES_PROIBIDOS)
    ):
        raise ErroAgenda("arquivo invalido")
    if tarefa["prioridade"] not in PRIORIDADES:
        raise ErroAgenda("arquivo invalido")
    prazo = tarefa["prazo"]
    if prazo is not None and (not isinstance(prazo, str) or not data_valida(prazo)):
        raise ErroAgenda("arquivo invalido")
    if type(tarefa["concluida"]) is not bool:
        raise ErroAgenda("arquivo invalido")


def validar_agenda(dados):
    if not isinstance(dados, dict) or set(dados) != CHAVES_RAIZ:
        raise ErroAgenda("arquivo invalido")
    tarefas = dados["tarefas"]
    if not isinstance(tarefas, list):
        raise ErroAgenda("arquivo invalido")
    ids = set()
    for tarefa in tarefas:
        validar_tarefa(tarefa)
        if tarefa["id"] in ids:
            raise ErroAgenda("arquivo invalido")
        ids.add(tarefa["id"])
    proximo_id = dados["proximo_id"]
    if type(proximo_id) is not int or proximo_id < 1:
        raise ErroAgenda("arquivo invalido")
    if ids and proximo_id <= max(ids):
        raise ErroAgenda("arquivo invalido")


def ler_agenda(caminho):
    try:
        with open(caminho, "rb") as arquivo:
            conteudo = arquivo.read().decode("utf-8")
        dados = json.loads(conteudo, object_pairs_hook=objeto_sem_duplicatas)
    except (OSError, UnicodeDecodeError, ValueError, RecursionError):
        raise ErroAgenda("arquivo invalido")
    validar_agenda(dados)
    return dados


def ler_agenda_existente(caminho):
    if not os.path.exists(caminho):
        raise ErroAgenda("arquivo inexistente")
    return ler_agenda(caminho)


def salvar_agenda(caminho, agenda):
    texto = json.dumps(agenda, indent=2, ensure_ascii=False) + "\n"
    try:
        conteudo = texto.encode("utf-8")
    except UnicodeEncodeError:
        raise ErroAgenda("titulo invalido")
    try:
        with open(caminho, "wb") as arquivo:
            arquivo.write(conteudo)
    except OSError:
        raise ErroAgenda("nao foi possivel gravar o arquivo")


def comando_adicionar(args):
    titulo = args.titulo.strip()
    if not titulo:
        raise ErroAgenda("titulo vazio")
    if any(caractere in titulo for caractere in CARACTERES_PROIBIDOS):
        raise ErroAgenda("titulo invalido")
    if args.prazo is not None and not data_valida(args.prazo):
        raise ErroAgenda("prazo invalido")

    if os.path.exists(args.arquivo):
        agenda = ler_agenda(args.arquivo)
    else:
        agenda = {"proximo_id": 1, "tarefas": []}

    id_novo = agenda["proximo_id"]
    agenda["tarefas"].append(
        {
            "id": id_novo,
            "titulo": titulo,
            "prioridade": args.prioridade,
            "prazo": args.prazo,
            "concluida": False,
        }
    )
    agenda["proximo_id"] = id_novo + 1
    salvar_agenda(args.arquivo, agenda)
    escrever_saida(f"ok id={id_novo}\n")
    return 0


def comando_listar(args):
    agenda = ler_agenda_existente(args.arquivo)
    tarefas = agenda["tarefas"]
    if args.prioridade is not None:
        tarefas = [t for t in tarefas if t["prioridade"] == args.prioridade]
    if args.somente_abertas:
        tarefas = [t for t in tarefas if not t["concluida"]]
    tarefas = sorted(tarefas, key=lambda t: (ORDEM_PRIORIDADE[t["prioridade"]], t["id"]))

    linhas = []
    for tarefa in tarefas:
        estado = "concluida" if tarefa["concluida"] else "aberta"
        prazo = tarefa["prazo"] or "-"
        linhas.append(
            f"{tarefa['id']}\t{tarefa['prioridade']}\t{estado}\t{prazo}\t{tarefa['titulo']}\n"
        )
    escrever_saida("".join(linhas))
    return 0


def comando_concluir(args):
    agenda = ler_agenda_existente(args.arquivo)
    tarefa = next((t for t in agenda["tarefas"] if t["id"] == args.id), None)
    if tarefa is None:
        raise ErroAgenda("id inexistente")
    if tarefa["concluida"]:
        raise ErroAgenda("ja concluida")
    tarefa["concluida"] = True
    salvar_agenda(args.arquivo, agenda)
    escrever_saida(f"ok id={args.id}\n")
    return 0


def construir_parser():
    parser = argparse.ArgumentParser(description="Agenda pessoal em linha de comando.")
    subcomandos = parser.add_subparsers(dest="comando", required=True, metavar="COMANDO")

    adicionar = subcomandos.add_parser("adicionar", help="adiciona uma tarefa")
    adicionar.add_argument("--titulo", required=True)
    adicionar.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    adicionar.add_argument("--prazo")
    adicionar.add_argument("--arquivo", required=True)
    adicionar.set_defaults(funcao=comando_adicionar)

    listar = subcomandos.add_parser("listar", help="lista tarefas")
    listar.add_argument("--prioridade", choices=PRIORIDADES)
    listar.add_argument("--somente-abertas", action="store_true")
    listar.add_argument("--arquivo", required=True)
    listar.set_defaults(funcao=comando_listar)

    concluir = subcomandos.add_parser("concluir", help="marca uma tarefa como concluida")
    concluir.add_argument("--id", required=True, type=int)
    concluir.add_argument("--arquivo", required=True)
    concluir.set_defaults(funcao=comando_concluir)

    return parser


def main(argv=None):
    args = construir_parser().parse_args(argv)
    try:
        return args.funcao(args)
    except ErroAgenda as erro:
        escrever_erro(str(erro))
        return 2


if __name__ == "__main__":
    sys.exit(main())
