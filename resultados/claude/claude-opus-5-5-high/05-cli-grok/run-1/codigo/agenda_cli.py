#!/usr/bin/env python3
"""CLI de agenda pessoal: adicionar, listar e concluir tarefas num arquivo JSON."""

import argparse
import datetime
import json
import os
import re
import sys
import tempfile

PRIORIDADES = ("baixa", "media", "alta")
ORDEM_PRIORIDADE = {"alta": 0, "media": 1, "baixa": 2}
CHAVES_RAIZ = {"proximo_id", "tarefas"}
CHAVES_TAREFA = ("id", "titulo", "prioridade", "prazo", "concluida")
CARACTERES_PROIBIDOS = ("\n", "\r", "\t")
RE_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
RE_INTEIRO = re.compile(r"[+-]?[0-9]+")


class ErroRegra(Exception):
    """Erro de regra de negócio: vira `erro: MENSAGEM` com código 2."""


class ArquivoInexistente(Exception):
    pass


# ---------------------------------------------------------------- validação

def eh_inteiro(valor):
    return type(valor) is int


def data_valida(texto):
    if type(texto) is not str or not RE_DATA.fullmatch(texto):
        return False
    try:
        datetime.date(int(texto[0:4]), int(texto[5:7]), int(texto[8:10]))
    except ValueError:
        return False
    return True


def titulo_normalizado(texto):
    """True se o título já está normalizado (sem espaços nas pontas etc.)."""
    if type(texto) is not str:
        return False
    if texto != texto.strip() or texto == "":
        return False
    if any(c in texto for c in CARACTERES_PROIBIDOS):
        return False
    try:
        texto.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def validar_tarefa(tarefa):
    if type(tarefa) is not dict or set(tarefa) != set(CHAVES_TAREFA):
        return False
    if not eh_inteiro(tarefa["id"]) or tarefa["id"] < 1:
        return False
    if not titulo_normalizado(tarefa["titulo"]):
        return False
    if type(tarefa["prioridade"]) is not str or tarefa["prioridade"] not in PRIORIDADES:
        return False
    if tarefa["prazo"] is not None and not data_valida(tarefa["prazo"]):
        return False
    if type(tarefa["concluida"]) is not bool:
        return False
    return True


def validar_dados(dados):
    if type(dados) is not dict or set(dados) != CHAVES_RAIZ:
        return False
    proximo = dados["proximo_id"]
    tarefas = dados["tarefas"]
    if not eh_inteiro(proximo) or proximo < 1:
        return False
    if type(tarefas) is not list:
        return False
    vistos = set()
    for tarefa in tarefas:
        if not validar_tarefa(tarefa):
            return False
        if tarefa["id"] in vistos:
            return False
        vistos.add(tarefa["id"])
    if vistos and proximo <= max(vistos):
        return False
    return True


# ---------------------------------------------------------------- arquivo

def _sem_chaves_duplicadas(pares):
    obj = {}
    for chave, valor in pares:
        if chave in obj:
            raise ValueError("chave duplicada")
        obj[chave] = valor
    return obj


def _rejeitar_constante(_nome):
    raise ValueError("constante nao permitida")


def carregar(caminho):
    try:
        with open(caminho, "rb") as f:
            bruto = f.read()
    except FileNotFoundError:
        raise ArquivoInexistente()
    except OSError:
        raise ErroRegra("arquivo invalido")
    try:
        texto = bruto.decode("utf-8")
        dados = json.loads(
            texto,
            object_pairs_hook=_sem_chaves_duplicadas,
            parse_constant=_rejeitar_constante,
        )
    except (ValueError, RecursionError):
        raise ErroRegra("arquivo invalido")
    if not validar_dados(dados):
        raise ErroRegra("arquivo invalido")
    return dados


def serializar(dados):
    canonico = {
        "proximo_id": dados["proximo_id"],
        "tarefas": [{chave: t[chave] for chave in CHAVES_TAREFA} for t in dados["tarefas"]],
    }
    return (json.dumps(canonico, indent=2, ensure_ascii=False) + "\n").encode("utf-8")


def gravar(caminho, dados):
    conteudo = serializar(dados)
    diretorio = os.path.dirname(os.path.abspath(caminho))
    fd, temporario = tempfile.mkstemp(prefix=".agenda-", suffix=".tmp", dir=diretorio)
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(conteudo)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporario, caminho)
    except BaseException:
        try:
            os.unlink(temporario)
        except OSError:
            pass
        raise


# ---------------------------------------------------------------- comandos

def escrever_stdout(texto):
    sys.stdout.buffer.write(texto.encode("utf-8"))
    sys.stdout.buffer.flush()


def cmd_adicionar(args):
    titulo = args.titulo.strip()
    if titulo == "":
        raise ErroRegra("titulo vazio")
    if not titulo_normalizado(titulo):
        raise ErroRegra("titulo invalido")
    if args.prazo is not None and not data_valida(args.prazo):
        raise ErroRegra("prazo invalido")

    try:
        dados = carregar(args.arquivo)
    except ArquivoInexistente:
        dados = {"proximo_id": 1, "tarefas": []}

    novo_id = dados["proximo_id"]
    dados["tarefas"].append({
        "id": novo_id,
        "titulo": titulo,
        "prioridade": args.prioridade,
        "prazo": args.prazo,
        "concluida": False,
    })
    dados["proximo_id"] = novo_id + 1
    try:
        gravar(args.arquivo, dados)
    except OSError:
        raise ErroRegra("arquivo invalido")
    escrever_stdout("ok id=%d\n" % novo_id)


def cmd_listar(args):
    try:
        dados = carregar(args.arquivo)
    except ArquivoInexistente:
        raise ErroRegra("arquivo inexistente")

    tarefas = dados["tarefas"]
    if args.prioridade is not None:
        tarefas = [t for t in tarefas if t["prioridade"] == args.prioridade]
    if args.somente_abertas:
        tarefas = [t for t in tarefas if not t["concluida"]]
    tarefas = sorted(tarefas, key=lambda t: (ORDEM_PRIORIDADE[t["prioridade"]], t["id"]))

    linhas = []
    for t in tarefas:
        linhas.append("\t".join((
            str(t["id"]),
            t["prioridade"],
            "concluida" if t["concluida"] else "aberta",
            t["prazo"] if t["prazo"] is not None else "-",
            t["titulo"],
        )) + "\n")
    if linhas:
        escrever_stdout("".join(linhas))


def cmd_concluir(args):
    try:
        dados = carregar(args.arquivo)
    except ArquivoInexistente:
        raise ErroRegra("arquivo inexistente")

    for tarefa in dados["tarefas"]:
        if tarefa["id"] == args.id:
            break
    else:
        raise ErroRegra("id inexistente")
    if tarefa["concluida"]:
        raise ErroRegra("ja concluida")

    tarefa["concluida"] = True
    try:
        gravar(args.arquivo, dados)
    except OSError:
        raise ErroRegra("arquivo invalido")
    escrever_stdout("ok id=%d\n" % tarefa["id"])


# ---------------------------------------------------------------- argparse

def tipo_inteiro(texto):
    if not RE_INTEIRO.fullmatch(texto):
        raise argparse.ArgumentTypeError("inteiro invalido: %r" % texto)
    return int(texto)


def criar_parser():
    parser = argparse.ArgumentParser(prog="agenda_cli.py", description="Agenda pessoal.",
                                     allow_abbrev=False)
    sub = parser.add_subparsers(dest="comando", metavar="COMANDO")
    sub.required = True

    p_add = sub.add_parser("adicionar", help="adiciona uma tarefa", allow_abbrev=False)
    p_add.add_argument("--titulo", required=True)
    p_add.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    p_add.add_argument("--prazo")
    p_add.add_argument("--arquivo", required=True)
    p_add.set_defaults(func=cmd_adicionar)

    p_list = sub.add_parser("listar", help="lista tarefas", allow_abbrev=False)
    p_list.add_argument("--arquivo", required=True)
    p_list.add_argument("--prioridade", choices=PRIORIDADES)
    p_list.add_argument("--somente-abertas", action="store_true")
    p_list.set_defaults(func=cmd_listar)

    p_conc = sub.add_parser("concluir", help="conclui uma tarefa", allow_abbrev=False)
    p_conc.add_argument("--id", required=True, type=tipo_inteiro)
    p_conc.add_argument("--arquivo", required=True)
    p_conc.set_defaults(func=cmd_concluir)

    return parser


def main(argv=None):
    args = criar_parser().parse_args(argv)
    try:
        args.func(args)
    except ErroRegra as erro:
        sys.stderr.write("erro: %s\n" % erro)
        sys.stderr.flush()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
