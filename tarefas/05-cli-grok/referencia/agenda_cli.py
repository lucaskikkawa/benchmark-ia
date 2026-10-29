"""Agenda pessoal em JSON, com três subcomandos."""

import argparse
import json
import sys
from datetime import date
from pathlib import Path

_PRIORIDADES = ("alta", "media", "baixa")
_ORDEM = {nome: indice for indice, nome in enumerate(_PRIORIDADES)}
_CHAVES_RAIZ = {"proximo_id", "tarefas"}
_CHAVES_TAREFA = {"id", "titulo", "prioridade", "prazo", "concluida"}


class ErroUso(Exception):
    """Erro de regra de negócio. A mensagem vai para stderr."""


def main(argv: list[str] | None = None) -> int:
    """Executa a CLI. Devolve 0 em sucesso e 2 em erro de regra."""
    parser = _parser()
    args = parser.parse_args(argv)
    try:
        if args.comando == "adicionar":
            _adicionar(args)
        elif args.comando == "listar":
            _listar(args)
        else:
            _concluir(args)
    except ErroUso as exc:
        print(f"erro: {exc}", file=sys.stderr)
        return 2
    return 0


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agenda_cli.py")
    sub = parser.add_subparsers(dest="comando", required=True)

    adicionar = sub.add_parser("adicionar", help="inclui uma tarefa")
    adicionar.add_argument("--titulo", required=True)
    adicionar.add_argument("--prioridade", required=True, choices=_PRIORIDADES)
    adicionar.add_argument("--prazo", default=None)
    adicionar.add_argument("--arquivo", required=True)

    listar = sub.add_parser("listar", help="lista tarefas")
    listar.add_argument("--arquivo", required=True)
    listar.add_argument("--prioridade", choices=_PRIORIDADES)
    listar.add_argument("--somente-abertas", action="store_true")

    concluir = sub.add_parser("concluir", help="marca uma tarefa como concluída")
    concluir.add_argument("--id", required=True, type=int)
    concluir.add_argument("--arquivo", required=True)
    return parser


def _adicionar(args: argparse.Namespace) -> None:
    titulo = args.titulo.strip()
    if titulo == "":
        raise ErroUso("titulo vazio")
    if any(caractere in titulo for caractere in "\n\r\t"):
        raise ErroUso("titulo invalido")
    prazo = None
    if args.prazo is not None:
        if not _data_valida(args.prazo):
            raise ErroUso("prazo invalido")
        prazo = args.prazo
    dados = _carregar(args.arquivo, criar=True)
    identificador = dados["proximo_id"]
    dados["tarefas"].append(
        {
            "id": identificador,
            "titulo": titulo,
            "prioridade": args.prioridade,
            "prazo": prazo,
            "concluida": False,
        }
    )
    dados["proximo_id"] = identificador + 1
    _gravar(args.arquivo, dados)
    print(f"ok id={identificador}")


def _listar(args: argparse.Namespace) -> None:
    dados = _carregar(args.arquivo, criar=False)
    tarefas = dados["tarefas"]
    if args.prioridade is not None:
        tarefas = [item for item in tarefas if item["prioridade"] == args.prioridade]
    if args.somente_abertas:
        tarefas = [item for item in tarefas if not item["concluida"]]
    tarefas = sorted(tarefas, key=lambda item: (_ORDEM[item["prioridade"]], item["id"]))
    for item in tarefas:
        estado = "concluida" if item["concluida"] else "aberta"
        prazo = item["prazo"] if item["prazo"] else "-"
        print(f"{item['id']}\t{item['prioridade']}\t{estado}\t{prazo}\t{item['titulo']}")


def _concluir(args: argparse.Namespace) -> None:
    dados = _carregar(args.arquivo, criar=False)
    for item in dados["tarefas"]:
        if item["id"] == args.id:
            if item["concluida"]:
                raise ErroUso("ja concluida")
            item["concluida"] = True
            _gravar(args.arquivo, dados)
            print(f"ok id={args.id}")
            return
    raise ErroUso("id inexistente")


def _carregar(caminho: str, criar: bool) -> dict:
    path = Path(caminho)
    if not path.exists():
        if criar:
            return {"proximo_id": 1, "tarefas": []}
        raise ErroUso("arquivo inexistente")
    try:
        dados = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ErroUso("arquivo invalido") from exc
    if not _valido(dados):
        raise ErroUso("arquivo invalido")
    return dados


def _gravar(caminho: str, dados: dict) -> None:
    texto = json.dumps(dados, ensure_ascii=False, indent=2) + "\n"
    Path(caminho).write_text(texto, encoding="utf-8")


def _valido(dados: object) -> bool:
    if not isinstance(dados, dict) or set(dados) != _CHAVES_RAIZ:
        return False
    proximo = dados["proximo_id"]
    tarefas = dados["tarefas"]
    if isinstance(proximo, bool) or not isinstance(proximo, int) or proximo < 1:
        return False
    if not isinstance(tarefas, list):
        return False
    vistos = set()
    for item in tarefas:
        if not isinstance(item, dict) or set(item) != _CHAVES_TAREFA:
            return False
        identificador = item["id"]
        if (
            isinstance(identificador, bool)
            or not isinstance(identificador, int)
            or identificador < 1
            or identificador in vistos
        ):
            return False
        vistos.add(identificador)
        titulo = item["titulo"]
        if (
            not isinstance(titulo, str)
            or titulo.strip() == ""
            or titulo != titulo.strip()
            or any(caractere in titulo for caractere in "\n\r\t")
        ):
            return False
        if item["prioridade"] not in _ORDEM:
            return False
        prazo = item["prazo"]
        if prazo is not None and not _data_valida(prazo):
            return False
        if not isinstance(item["concluida"], bool):
            return False
    if vistos and proximo <= max(vistos):
        return False
    return True


def _data_valida(texto: object) -> bool:
    if not isinstance(texto, str) or len(texto) != 10:
        return False
    try:
        return date.fromisoformat(texto).isoformat() == texto
    except ValueError:
        return False


if __name__ == "__main__":
    sys.exit(main())
