"""Agenda pessoal em JSON, acessível por subcomandos."""

import argparse
import datetime
import json
import re
import sys


PRIORIDADES = ("baixa", "media", "alta")
CAMPOS_TAREFA = {"id", "titulo", "prioridade", "prazo", "concluida"}


class ErroAgenda(Exception):
    """Erro de regra que deve ser apresentado sem traceback."""


def data_valida(valor):
    if not isinstance(valor, str) or not re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", valor):
        return False
    try:
        datetime.date.fromisoformat(valor)
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


def inteiro_positivo(valor):
    return type(valor) is int and valor >= 1


def objeto_sem_duplicatas(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError("chave duplicada")
        objeto[chave] = valor
    return objeto


def validar_agenda(agenda):
    if not isinstance(agenda, dict) or set(agenda) != {"proximo_id", "tarefas"}:
        return False
    if not inteiro_positivo(agenda["proximo_id"]) or not isinstance(agenda["tarefas"], list):
        return False
    ids = set()
    for tarefa in agenda["tarefas"]:
        if not isinstance(tarefa, dict) or set(tarefa) != CAMPOS_TAREFA:
            return False
        identificador = tarefa["id"]
        if not inteiro_positivo(identificador) or identificador in ids:
            return False
        if identificador >= agenda["proximo_id"]:
            return False
        ids.add(identificador)
        if not titulo_valido(tarefa["titulo"]):
            return False
        if tarefa["prioridade"] not in PRIORIDADES:
            return False
        if tarefa["prazo"] is not None and not data_valida(tarefa["prazo"]):
            return False
        if type(tarefa["concluida"]) is not bool:
            return False
    return True


def ler_agenda(caminho, permitir_novo=False):
    try:
        with open(caminho, encoding="utf-8") as arquivo:
            agenda = json.load(arquivo, object_pairs_hook=objeto_sem_duplicatas)
    except FileNotFoundError:
        if permitir_novo:
            return {"proximo_id": 1, "tarefas": []}
        raise ErroAgenda("arquivo inexistente") from None
    except (OSError, ValueError, RecursionError):
        raise ErroAgenda("arquivo invalido") from None
    if not validar_agenda(agenda):
        raise ErroAgenda("arquivo invalido")
    return agenda


def gravar_agenda(caminho, agenda):
    try:
        with open(caminho, "w", encoding="utf-8", newline="\n") as arquivo:
            json.dump(agenda, arquivo, indent=2, ensure_ascii=False)
            arquivo.write("\n")
    except (OSError, UnicodeError):
        raise ErroAgenda("arquivo invalido") from None


def criar_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    comandos = parser.add_subparsers(dest="comando", required=True)

    adicionar = comandos.add_parser("adicionar")
    adicionar.add_argument("--titulo", required=True)
    adicionar.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    adicionar.add_argument("--prazo")
    adicionar.add_argument("--arquivo", required=True)

    listar = comandos.add_parser("listar")
    listar.add_argument("--arquivo", required=True)
    listar.add_argument("--prioridade", choices=PRIORIDADES)
    listar.add_argument("--somente-abertas", action="store_true")

    concluir = comandos.add_parser("concluir")
    concluir.add_argument("--id", required=True, type=int)
    concluir.add_argument("--arquivo", required=True)
    return parser


def executar(args):
    agenda = ler_agenda(args.arquivo, permitir_novo=args.comando == "adicionar")
    if args.comando == "adicionar":
        titulo = args.titulo.strip()
        if not titulo:
            raise ErroAgenda("titulo vazio")
        if not titulo_valido(titulo):
            raise ErroAgenda("titulo invalido")
        if args.prazo is not None and not data_valida(args.prazo):
            raise ErroAgenda("prazo invalido")
        identificador = agenda["proximo_id"]
        agenda["tarefas"].append({
            "id": identificador,
            "titulo": titulo,
            "prioridade": args.prioridade,
            "prazo": args.prazo,
            "concluida": False,
        })
        agenda["proximo_id"] += 1
        gravar_agenda(args.arquivo, agenda)
        print(f"ok id={identificador}")
    elif args.comando == "listar":
        ordem = {"alta": 0, "media": 1, "baixa": 2}
        for tarefa in sorted(agenda["tarefas"], key=lambda t: (ordem[t["prioridade"]], t["id"])):
            if args.prioridade is not None and tarefa["prioridade"] != args.prioridade:
                continue
            if args.somente_abertas and tarefa["concluida"]:
                continue
            estado = "concluida" if tarefa["concluida"] else "aberta"
            prazo = tarefa["prazo"] if tarefa["prazo"] is not None else "-"
            print(f'{tarefa["id"]}\t{tarefa["prioridade"]}\t{estado}\t{prazo}\t{tarefa["titulo"]}')
    else:
        tarefa = next((t for t in agenda["tarefas"] if t["id"] == args.id), None)
        if tarefa is None:
            raise ErroAgenda("id inexistente")
        if tarefa["concluida"]:
            raise ErroAgenda("ja concluida")
        tarefa["concluida"] = True
        gravar_agenda(args.arquivo, agenda)
        print(f"ok id={args.id}")


def main():
    args = criar_parser().parse_args()
    try:
        executar(args)
    except ErroAgenda as erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
