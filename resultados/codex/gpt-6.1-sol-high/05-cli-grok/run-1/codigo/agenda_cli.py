"""Agenda pessoal com subcomandos e armazenamento em JSON."""

import argparse
import datetime
import json
import re
import sys
from pathlib import Path


PRIORIDADES = ("baixa", "media", "alta")
ORDEM_PRIORIDADE = {"alta": 0, "media": 1, "baixa": 2}
CHAVES_TAREFA = {"id", "titulo", "prioridade", "prazo", "concluida"}


class ErroAgenda(Exception):
    """Erro de regra apresentado sem traceback."""


def prazo_valido(prazo):
    if not isinstance(prazo, str):
        return False
    if re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", prazo) is None:
        return False
    try:
        datetime.date.fromisoformat(prazo)
    except ValueError:
        return False
    return True


def titulo_valido(titulo):
    return (
        isinstance(titulo, str)
        and bool(titulo)
        and titulo == titulo.strip()
        and not any(caractere in titulo for caractere in "\n\r\t")
    )


def validar_agenda(agenda):
    if not isinstance(agenda, dict) or set(agenda) != {"proximo_id", "tarefas"}:
        return False
    proximo_id = agenda["proximo_id"]
    if type(proximo_id) is not int or proximo_id < 1:
        return False
    if not isinstance(agenda["tarefas"], list):
        return False

    ids = set()
    for tarefa in agenda["tarefas"]:
        if not isinstance(tarefa, dict) or set(tarefa) != CHAVES_TAREFA:
            return False
        identificador = tarefa["id"]
        if (
            type(identificador) is not int
            or identificador < 1
            or identificador >= proximo_id
            or identificador in ids
        ):
            return False
        ids.add(identificador)
        if not titulo_valido(tarefa["titulo"]):
            return False
        if tarefa["prioridade"] not in PRIORIDADES:
            return False
        if tarefa["prazo"] is not None and not prazo_valido(tarefa["prazo"]):
            return False
        if type(tarefa["concluida"]) is not bool:
            return False
    return True


def objeto_sem_duplicatas(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError("chave duplicada")
        objeto[chave] = valor
    return objeto


def carregar(caminho, criar=False):
    try:
        with caminho.open("r", encoding="utf-8") as arquivo:
            agenda = json.load(arquivo, object_pairs_hook=objeto_sem_duplicatas)
    except FileNotFoundError:
        if criar:
            return {"proximo_id": 1, "tarefas": []}
        raise ErroAgenda("arquivo inexistente") from None
    except (OSError, UnicodeError, ValueError, RecursionError):
        raise ErroAgenda("arquivo invalido") from None
    if not validar_agenda(agenda):
        raise ErroAgenda("arquivo invalido")
    return agenda


def salvar(caminho, agenda):
    try:
        with caminho.open("w", encoding="utf-8", newline="\n") as arquivo:
            json.dump(agenda, arquivo, indent=2, ensure_ascii=False)
            arquivo.write("\n")
    except (OSError, UnicodeError):
        raise ErroAgenda("arquivo invalido") from None


def adicionar(args, caminho, agenda):
    titulo = args.titulo.strip()
    if not titulo:
        raise ErroAgenda("titulo vazio")
    if not titulo_valido(titulo):
        raise ErroAgenda("titulo invalido")
    if args.prazo is not None and not prazo_valido(args.prazo):
        raise ErroAgenda("prazo invalido")

    identificador = agenda["proximo_id"]
    agenda["tarefas"].append(
        {
            "id": identificador,
            "titulo": titulo,
            "prioridade": args.prioridade,
            "prazo": args.prazo,
            "concluida": False,
        }
    )
    agenda["proximo_id"] += 1
    salvar(caminho, agenda)
    print(f"ok id={identificador}")


def listar(args, agenda):
    tarefas = sorted(
        agenda["tarefas"],
        key=lambda tarefa: (ORDEM_PRIORIDADE[tarefa["prioridade"]], tarefa["id"]),
    )
    for tarefa in tarefas:
        if args.prioridade is not None and tarefa["prioridade"] != args.prioridade:
            continue
        if args.somente_abertas and tarefa["concluida"]:
            continue
        estado = "concluida" if tarefa["concluida"] else "aberta"
        prazo = tarefa["prazo"] if tarefa["prazo"] is not None else "-"
        print(
            f"{tarefa['id']}\t{tarefa['prioridade']}\t{estado}\t"
            f"{prazo}\t{tarefa['titulo']}"
        )


def concluir(args, caminho, agenda):
    for tarefa in agenda["tarefas"]:
        if tarefa["id"] == args.id:
            if tarefa["concluida"]:
                raise ErroAgenda("ja concluida")
            tarefa["concluida"] = True
            salvar(caminho, agenda)
            print(f"ok id={tarefa['id']}")
            return
    raise ErroAgenda("id inexistente")


def criar_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subcomandos = parser.add_subparsers(dest="comando", required=True)

    parser_adicionar = subcomandos.add_parser("adicionar")
    parser_adicionar.add_argument("--titulo", required=True)
    parser_adicionar.add_argument("--prioridade", choices=PRIORIDADES, required=True)
    parser_adicionar.add_argument("--prazo")

    parser_listar = subcomandos.add_parser("listar")
    parser_listar.add_argument("--prioridade", choices=PRIORIDADES)
    parser_listar.add_argument("--somente-abertas", action="store_true")

    parser_concluir = subcomandos.add_parser("concluir")
    parser_concluir.add_argument("--id", type=int, required=True)

    for subparser in (parser_adicionar, parser_listar, parser_concluir):
        subparser.add_argument("--arquivo", required=True)
    return parser


def main(argv=None):
    args = criar_parser().parse_args(argv)
    caminho = Path(args.arquivo)
    try:
        agenda = carregar(caminho, criar=args.comando == "adicionar")
        if args.comando == "adicionar":
            adicionar(args, caminho, agenda)
        elif args.comando == "listar":
            listar(args, agenda)
        else:
            concluir(args, caminho, agenda)
    except ErroAgenda as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
