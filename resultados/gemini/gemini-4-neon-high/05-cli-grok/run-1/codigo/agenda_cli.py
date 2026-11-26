#!/usr/bin/env python3
"""CLI de agenda pessoal."""

from __future__ import annotations

import argparse
import datetime
import json
from pathlib import Path
import re
import sys
from typing import Any, NoReturn

PRIORIDADES = ("baixa", "media", "alta")
PRIORIDADE_ORDEM = {"alta": 0, "media": 1, "baixa": 2}
CHAVES_RAIZ = {"proximo_id", "tarefas"}
CHAVES_TAREFA = {"id", "titulo", "prioridade", "prazo", "concluida"}
REGEX_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")
CARACTERES_PROIBIDOS_TITULO = ("\n", "\r", "\t")


class ErroRegra(Exception):
    """Erro de regra de negocio que encerra o programa com codigo 2."""


def encerrar_erro(mensagem: str) -> NoReturn:
    sys.stderr.write(f"erro: {mensagem}\n")
    sys.exit(2)


def data_valida(texto: Any) -> bool:
    if type(texto) is not str:
        return False
    if REGEX_DATA.fullmatch(texto) is None:
        return False
    ano = int(texto[0:4])
    mes = int(texto[5:7])
    dia = int(texto[8:10])
    try:
        datetime.date(ano, mes, dia)
    except ValueError:
        return False
    return True


def _objeto_sem_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in obj:
            raise ValueError("chave duplicada")
        obj[chave] = valor
    return obj


def _rejeitar_constante(_constante: str) -> NoReturn:
    raise ValueError("constante JSON invalida")


def validar_estrutura(dados: Any) -> dict[str, Any]:
    if type(dados) is not dict or set(dados.keys()) != CHAVES_RAIZ:
        raise ErroRegra("arquivo invalido")

    proximo_id = dados["proximo_id"]
    if type(proximo_id) is not int or proximo_id < 1:
        raise ErroRegra("arquivo invalido")

    tarefas = dados["tarefas"]
    if type(tarefas) is not list:
        raise ErroRegra("arquivo invalido")

    ids_vistos: set[int] = set()
    for tarefa in tarefas:
        if type(tarefa) is not dict or set(tarefa.keys()) != CHAVES_TAREFA:
            raise ErroRegra("arquivo invalido")

        tarefa_id = tarefa["id"]
        if type(tarefa_id) is not int or tarefa_id < 1:
            raise ErroRegra("arquivo invalido")
        if tarefa_id in ids_vistos or tarefa_id >= proximo_id:
            raise ErroRegra("arquivo invalido")
        ids_vistos.add(tarefa_id)

        titulo = tarefa["titulo"]
        if type(titulo) is not str or not titulo:
            raise ErroRegra("arquivo invalido")
        if titulo != titulo.strip():
            raise ErroRegra("arquivo invalido")
        if any(ch in titulo for ch in CARACTERES_PROIBIDOS_TITULO):
            raise ErroRegra("arquivo invalido")

        prioridade = tarefa["prioridade"]
        if type(prioridade) is not str or prioridade not in PRIORIDADES:
            raise ErroRegra("arquivo invalido")

        prazo = tarefa["prazo"]
        if prazo is not None and not data_valida(prazo):
            raise ErroRegra("arquivo invalido")

        concluida = tarefa["concluida"]
        if type(concluida) is not bool:
            raise ErroRegra("arquivo invalido")

    return dados


def carregar_arquivo(caminho: str, *, permitir_inexistente: bool = False) -> dict[str, Any]:
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            conteudo = arquivo.read()
    except FileNotFoundError:
        if permitir_inexistente:
            return {"proximo_id": 1, "tarefas": []}
        raise ErroRegra("arquivo inexistente") from None
    except (OSError, UnicodeDecodeError):
        raise ErroRegra("arquivo invalido") from None

    try:
        dados = json.loads(
            conteudo,
            object_pairs_hook=_objeto_sem_duplicadas,
            parse_constant=_rejeitar_constante,
        )
    except (json.JSONDecodeError, ValueError):
        raise ErroRegra("arquivo invalido") from None

    return validar_estrutura(dados)


def salvar_arquivo(caminho: str, dados: dict[str, Any]) -> None:
    conteudo = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"
    destino = Path(caminho)
    if destino.parent != Path("."):
        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
        except OSError:
            raise ErroRegra("arquivo invalido") from None
    try:
        with open(caminho, "w", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(conteudo)
    except OSError:
        raise ErroRegra("arquivo invalido") from None


def cmd_adicionar(args: argparse.Namespace) -> None:
    titulo = args.titulo.strip()
    if not titulo:
        raise ErroRegra("titulo vazio")
    if any(ch in titulo for ch in CARACTERES_PROIBIDOS_TITULO):
        raise ErroRegra("titulo invalido")

    prazo: str | None = args.prazo
    if prazo is not None and not data_valida(prazo):
        raise ErroRegra("prazo invalido")

    dados = carregar_arquivo(args.arquivo, permitir_inexistente=True)
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
    dados = carregar_arquivo(args.arquivo, permitir_inexistente=False)
    tarefas = dados["tarefas"]

    if args.prioridade is not None:
        tarefas = [t for t in tarefas if t["prioridade"] == args.prioridade]
    if args.somente_abertas:
        tarefas = [t for t in tarefas if not t["concluida"]]

    tarefas_ordenadas = sorted(
        tarefas,
        key=lambda t: (PRIORIDADE_ORDEM[t["prioridade"]], t["id"]),
    )

    linhas = []
    for tarefa in tarefas_ordenadas:
        estado = "concluida" if tarefa["concluida"] else "aberta"
        prazo = tarefa["prazo"] if tarefa["prazo"] is not None else "-"
        linhas.append(
            f"{tarefa['id']}\t{tarefa['prioridade']}\t{estado}\t{prazo}\t{tarefa['titulo']}\n"
        )

    if linhas:
        sys.stdout.write("".join(linhas))


def cmd_concluir(args: argparse.Namespace) -> None:
    dados = carregar_arquivo(args.arquivo, permitir_inexistente=False)
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
    sys.stdout.write(f"ok id={args.id}\n")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agenda_cli.py")
    subparsers = parser.add_subparsers(dest="comando", required=True)

    p_adicionar = subparsers.add_parser("adicionar")
    p_adicionar.add_argument("--titulo", required=True)
    p_adicionar.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    p_adicionar.add_argument("--prazo", default=None)
    p_adicionar.add_argument("--arquivo", required=True)
    p_adicionar.set_defaults(func=cmd_adicionar)

    p_listar = subparsers.add_parser("listar")
    p_listar.add_argument("--arquivo", required=True)
    p_listar.add_argument("--prioridade", default=None, choices=PRIORIDADES)
    p_listar.add_argument("--somente-abertas", action="store_true")
    p_listar.set_defaults(func=cmd_listar)

    p_concluir = subparsers.add_parser("concluir")
    p_concluir.add_argument("--id", required=True, type=int)
    p_concluir.add_argument("--arquivo", required=True)
    p_concluir.set_defaults(func=cmd_concluir)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = construir_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ErroRegra as exc:
        encerrar_erro(str(exc))


if __name__ == "__main__":
    main()
