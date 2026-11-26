#!/usr/bin/env python3
"""CLI de agenda pessoal usando apenas a biblioteca padrao."""

from __future__ import annotations

import argparse
from datetime import date
import json
from pathlib import Path
import re
import sys
from typing import Any

PRIORIDADES = ("baixa", "media", "alta")
ORDEM_PRIORIDADE = {"alta": 0, "media": 1, "baixa": 2}
CHAVES_RAIZ = {"proximo_id", "tarefas"}
CHAVES_TAREFA = {"id", "titulo", "prioridade", "prazo", "concluida"}
RE_DATA = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


class ErroRegra(Exception):
    """Erro de validacao ou regra de negocio."""


def validar_prazo(valor: str, mensagem_erro: str = "prazo invalido") -> str:
    """Valida e retorna uma data real YYYY-MM-DD, ou lanca ErroRegra."""
    if not RE_DATA.fullmatch(valor):
        raise ErroRegra(mensagem_erro)
    ano, mes, dia = map(int, valor.split("-"))
    try:
        date(ano, mes, dia)
    except ValueError as exc:
        raise ErroRegra(mensagem_erro) from exc
    return valor


def validar_titulo_entrada(texto: str) -> str:
    """Normaliza e valida o titulo informado na CLI."""
    titulo = texto.strip()
    if not titulo:
        raise ErroRegra("titulo vazio")
    if "\n" in titulo or "\r" in titulo or "\t" in titulo:
        raise ErroRegra("titulo invalido")
    return titulo


def _sem_chaves_duplicadas(pares: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for chave, valor in pares:
        if chave in obj:
            raise ValueError("chave duplicada")
        obj[chave] = valor
    return obj


def _rejeitar_constante(_: str) -> Any:
    raise ValueError("constante JSON invalida")


def _eh_int_estrito(valor: Any) -> bool:
    return isinstance(valor, int) and not isinstance(valor, bool)


def _validar_prazo_arquivo(valor: Any) -> None:
    if valor is None:
        return
    if not isinstance(valor, str):
        raise ErroRegra("arquivo invalido")
    validar_prazo(valor, "arquivo invalido")


def validar_estrutura_arquivo(dados: Any) -> dict[str, Any]:
    """Valida o schema completo e as invariantes do JSON da agenda."""
    if not isinstance(dados, dict) or set(dados.keys()) != CHAVES_RAIZ:
        raise ErroRegra("arquivo invalido")

    proximo_id = dados["proximo_id"]
    if not _eh_int_estrito(proximo_id) or proximo_id < 1:
        raise ErroRegra("arquivo invalido")

    tarefas = dados["tarefas"]
    if not isinstance(tarefas, list):
        raise ErroRegra("arquivo invalido")

    ids_vistos: set[int] = set()
    for tarefa in tarefas:
        if not isinstance(tarefa, dict) or set(tarefa.keys()) != CHAVES_TAREFA:
            raise ErroRegra("arquivo invalido")

        tid = tarefa["id"]
        if not _eh_int_estrito(tid) or tid < 1 or tid in ids_vistos or tid >= proximo_id:
            raise ErroRegra("arquivo invalido")
        ids_vistos.add(tid)

        titulo = tarefa["titulo"]
        if (
            not isinstance(titulo, str)
            or not titulo
            or titulo.strip() != titulo
            or "\n" in titulo
            or "\r" in titulo
            or "\t" in titulo
        ):
            raise ErroRegra("arquivo invalido")

        prioridade = tarefa["prioridade"]
        if not isinstance(prioridade, str) or prioridade not in PRIORIDADES:
            raise ErroRegra("arquivo invalido")

        _validar_prazo_arquivo(tarefa["prazo"])

        if not isinstance(tarefa["concluida"], bool):
            raise ErroRegra("arquivo invalido")

    return dados


def ler_arquivo(caminho: Path, permitir_ausente: bool = False) -> dict[str, Any]:
    """Le e valida o arquivo JSON da agenda."""
    if not caminho.exists():
        if permitir_ausente:
            return {"proximo_id": 1, "tarefas": []}
        raise ErroRegra("arquivo inexistente")

    try:
        conteudo = caminho.read_text(encoding="utf-8")
        dados = json.loads(
            conteudo,
            object_pairs_hook=_sem_chaves_duplicadas,
            parse_constant=_rejeitar_constante,
        )
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ErroRegra("arquivo invalido") from exc

    return validar_estrutura_arquivo(dados)


def gravar_arquivo(caminho: Path, dados: dict[str, Any]) -> None:
    """Grava o dicionario da agenda em UTF-8 formatado com quebra final."""
    texto = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"
    with caminho.open("w", encoding="utf-8", newline="\n") as fh:
        fh.write(texto)


def cmd_adicionar(args: argparse.Namespace) -> None:
    titulo = validar_titulo_entrada(args.titulo)
    prazo = validar_prazo(args.prazo) if args.prazo is not None else None
    caminho = Path(args.arquivo)

    dados = ler_arquivo(caminho, permitir_ausente=True)
    novo_id = dados["proximo_id"]
    dados["proximo_id"] = novo_id + 1
    dados["tarefas"].append(
        {
            "id": novo_id,
            "titulo": titulo,
            "prioridade": args.prioridade,
            "prazo": prazo,
            "concluida": False,
        }
    )

    gravar_arquivo(caminho, dados)
    sys.stdout.write(f"ok id={novo_id}\n")


def cmd_listar(args: argparse.Namespace) -> None:
    dados = ler_arquivo(Path(args.arquivo), permitir_ausente=False)
    tarefas = dados["tarefas"]

    if args.prioridade is not None:
        tarefas = [t for t in tarefas if t["prioridade"] == args.prioridade]
    if args.somente_abertas:
        tarefas = [t for t in tarefas if not t["concluida"]]

    tarefas.sort(key=lambda t: (ORDEM_PRIORIDADE[t["prioridade"]], t["id"]))

    linhas = []
    for t in tarefas:
        estado = "concluida" if t["concluida"] else "aberta"
        prazo = t["prazo"] if t["prazo"] is not None else "-"
        linhas.append(f"{t['id']}\t{t['prioridade']}\t{estado}\t{prazo}\t{t['titulo']}\n")

    if linhas:
        sys.stdout.write("".join(linhas))


def cmd_concluir(args: argparse.Namespace) -> None:
    caminho = Path(args.arquivo)
    dados = ler_arquivo(caminho, permitir_ausente=False)

    alvo = next((t for t in dados["tarefas"] if t["id"] == args.id), None)
    if alvo is None:
        raise ErroRegra("id inexistente")
    if alvo["concluida"]:
        raise ErroRegra("ja concluida")

    alvo["concluida"] = True
    gravar_arquivo(caminho, dados)
    sys.stdout.write(f"ok id={args.id}\n")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agenda_cli.py")
    subparsers = parser.add_subparsers(dest="subcomando", required=True)

    p_add = subparsers.add_parser("adicionar")
    p_add.add_argument("--titulo", required=True)
    p_add.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    p_add.add_argument("--prazo")
    p_add.add_argument("--arquivo", required=True)
    p_add.set_defaults(func=cmd_adicionar)

    p_list = subparsers.add_parser("listar")
    p_list.add_argument("--arquivo", required=True)
    p_list.add_argument("--prioridade", choices=PRIORIDADES)
    p_list.add_argument("--somente-abertas", action="store_true")
    p_list.set_defaults(func=cmd_listar)

    p_done = subparsers.add_parser("concluir")
    p_done.add_argument("--id", required=True, type=int)
    p_done.add_argument("--arquivo", required=True)
    p_done.set_defaults(func=cmd_concluir)

    return parser


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = construir_parser()
    args = parser.parse_args(argv)
    try:
        args.func(args)
    except ErroRegra as exc:
        sys.stderr.write(f"erro: {exc}\n")
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
