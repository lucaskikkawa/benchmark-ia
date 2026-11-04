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
CHAVES_TAREFA = {"id", "titulo", "prioridade", "prazo", "concluida"}
RE_PRAZO = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
CARACTERES_PROIBIDOS = ("\n", "\r", "\t")


class ErroRegra(Exception):
    pass


def falhar(mensagem):
    raise ErroRegra(mensagem)


def eh_inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def prazo_valido(texto):
    if not isinstance(texto, str) or not RE_PRAZO.fullmatch(texto):
        return False
    try:
        datetime.date(int(texto[0:4]), int(texto[5:7]), int(texto[8:10]))
    except ValueError:
        return False
    return True


def codificavel(texto):
    try:
        texto.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def titulo_valido(titulo):
    return (
        isinstance(titulo, str)
        and titulo != ""
        and titulo == titulo.strip()
        and not any(c in titulo for c in CARACTERES_PROIBIDOS)
        and codificavel(titulo)
    )


def sem_chaves_duplicadas(pares):
    resultado = {}
    for chave, valor in pares:
        if chave in resultado:
            raise ValueError("chave duplicada")
        resultado[chave] = valor
    return resultado


def rejeitar_constante(_):
    raise ValueError("constante nao permitida")


def validar_dados(dados):
    if not isinstance(dados, dict) or set(dados) != CHAVES_RAIZ:
        return False
    proximo_id = dados["proximo_id"]
    tarefas = dados["tarefas"]
    if not eh_inteiro(proximo_id) or proximo_id < 1:
        return False
    if not isinstance(tarefas, list):
        return False
    ids = set()
    for tarefa in tarefas:
        if not isinstance(tarefa, dict) or set(tarefa) != CHAVES_TAREFA:
            return False
        tid = tarefa["id"]
        if not eh_inteiro(tid) or tid < 1 or tid in ids or tid >= proximo_id:
            return False
        ids.add(tid)
        if not titulo_valido(tarefa["titulo"]):
            return False
        if tarefa["prioridade"] not in PRIORIDADES or not isinstance(tarefa["prioridade"], str):
            return False
        if tarefa["prazo"] is not None and not prazo_valido(tarefa["prazo"]):
            return False
        if not isinstance(tarefa["concluida"], bool):
            return False
    return True


def carregar(caminho):
    try:
        with open(caminho, "rb") as f:
            bruto = f.read()
        texto = bruto.decode("utf-8")
        dados = json.loads(
            texto,
            object_pairs_hook=sem_chaves_duplicadas,
            parse_constant=rejeitar_constante,
        )
    except (OSError, ValueError, RecursionError):
        falhar("arquivo invalido")
    if not validar_dados(dados):
        falhar("arquivo invalido")
    return dados


def salvar(caminho, dados):
    conteudo = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"
    dados_bytes = conteudo.encode("utf-8")
    diretorio = os.path.dirname(os.path.abspath(caminho))
    fd, temporario = tempfile.mkstemp(dir=diretorio, prefix=".agenda-", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(dados_bytes)
            f.flush()
            os.fsync(f.fileno())
        os.replace(temporario, caminho)
    except BaseException:
        try:
            os.unlink(temporario)
        except OSError:
            pass
        raise


def exigir_existente(caminho):
    if not os.path.exists(caminho):
        falhar("arquivo inexistente")


def escrever_saida(texto):
    sys.stdout.buffer.write(texto.encode("utf-8"))
    sys.stdout.buffer.flush()


def cmd_adicionar(args):
    titulo = args.titulo.strip()
    if titulo == "":
        falhar("titulo vazio")
    if any(c in titulo for c in CARACTERES_PROIBIDOS) or not codificavel(titulo):
        falhar("titulo invalido")
    if args.prazo is not None and not prazo_valido(args.prazo):
        falhar("prazo invalido")

    if os.path.exists(args.arquivo):
        dados = carregar(args.arquivo)
    else:
        dados = {"proximo_id": 1, "tarefas": []}

    novo_id = dados["proximo_id"]
    dados["tarefas"].append(
        {
            "id": novo_id,
            "titulo": titulo,
            "prioridade": args.prioridade,
            "prazo": args.prazo,
            "concluida": False,
        }
    )
    dados["proximo_id"] = novo_id + 1
    salvar(args.arquivo, dados)
    escrever_saida("ok id=%d\n" % novo_id)


def cmd_listar(args):
    exigir_existente(args.arquivo)
    dados = carregar(args.arquivo)
    tarefas = dados["tarefas"]
    if args.prioridade is not None:
        tarefas = [t for t in tarefas if t["prioridade"] == args.prioridade]
    if args.somente_abertas:
        tarefas = [t for t in tarefas if not t["concluida"]]
    tarefas = sorted(tarefas, key=lambda t: (ORDEM_PRIORIDADE[t["prioridade"]], t["id"]))
    linhas = []
    for t in tarefas:
        estado = "concluida" if t["concluida"] else "aberta"
        prazo = t["prazo"] if t["prazo"] is not None else "-"
        linhas.append("%d\t%s\t%s\t%s\t%s\n" % (t["id"], t["prioridade"], estado, prazo, t["titulo"]))
    if linhas:
        escrever_saida("".join(linhas))


def cmd_concluir(args):
    exigir_existente(args.arquivo)
    dados = carregar(args.arquivo)
    for tarefa in dados["tarefas"]:
        if tarefa["id"] == args.id:
            if tarefa["concluida"]:
                falhar("ja concluida")
            tarefa["concluida"] = True
            salvar(args.arquivo, dados)
            escrever_saida("ok id=%d\n" % tarefa["id"])
            return
    falhar("id inexistente")


def montar_parser():
    parser = argparse.ArgumentParser(prog="agenda_cli.py", description="Agenda pessoal")
    sub = parser.add_subparsers(dest="comando")
    sub.required = True

    p_add = sub.add_parser("adicionar", help="adiciona uma tarefa")
    p_add.add_argument("--titulo", required=True)
    p_add.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    p_add.add_argument("--prazo")
    p_add.add_argument("--arquivo", required=True)
    p_add.set_defaults(func=cmd_adicionar)

    p_list = sub.add_parser("listar", help="lista tarefas")
    p_list.add_argument("--arquivo", required=True)
    p_list.add_argument("--prioridade", choices=PRIORIDADES)
    p_list.add_argument("--somente-abertas", action="store_true")
    p_list.set_defaults(func=cmd_listar)

    p_conc = sub.add_parser("concluir", help="conclui uma tarefa")
    p_conc.add_argument("--id", required=True, type=int)
    p_conc.add_argument("--arquivo", required=True)
    p_conc.set_defaults(func=cmd_concluir)

    return parser


def main(argv=None):
    args = montar_parser().parse_args(argv)
    try:
        args.func(args)
    except ErroRegra as erro:
        sys.stderr.write("erro: %s\n" % erro)
        sys.stderr.flush()
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
