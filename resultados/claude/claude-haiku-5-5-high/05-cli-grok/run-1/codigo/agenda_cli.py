"""CLI de agenda pessoal com arquivo JSON. Usa apenas a biblioteca padrão."""

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
_DATA = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2}")


class ErroAgenda(Exception):
    """Erro de regra: vira `erro: MENSAGEM` no stderr com código 2."""


def _eh_inteiro(valor):
    return isinstance(valor, int) and not isinstance(valor, bool)


def _titulo_gravavel(titulo):
    """Sem quebras/tabs e codificável em UTF-8 (argv ou JSON podem trazer surrogates)."""
    if any(c in titulo for c in "\n\r\t"):
        return False
    try:
        titulo.encode("utf-8")
    except UnicodeEncodeError:
        return False
    return True


def _data_valida(texto):
    if not isinstance(texto, str) or not _DATA.fullmatch(texto):
        return False
    try:
        datetime.date.fromisoformat(texto)
    except ValueError:
        return False
    return True


def _recusar_constante(nome):
    # NaN e Infinity não são JSON válido para este formato.
    raise ValueError(nome)


def _objeto_sem_chaves_repetidas(pares):
    objeto = {}
    for chave, valor in pares:
        if chave in objeto:
            raise ValueError(chave)
        objeto[chave] = valor
    return objeto


def validar(dados):
    if not isinstance(dados, dict) or set(dados) != CHAVES_RAIZ:
        raise ErroAgenda("arquivo invalido")

    proximo_id = dados["proximo_id"]
    tarefas = dados["tarefas"]
    if not _eh_inteiro(proximo_id) or proximo_id < 1 or not isinstance(tarefas, list):
        raise ErroAgenda("arquivo invalido")

    ids = set()
    for tarefa in tarefas:
        if not isinstance(tarefa, dict) or set(tarefa) != CHAVES_TAREFA:
            raise ErroAgenda("arquivo invalido")

        id_tarefa = tarefa["id"]
        titulo = tarefa["titulo"]
        prazo = tarefa["prazo"]
        if not _eh_inteiro(id_tarefa) or id_tarefa < 1 or id_tarefa in ids or id_tarefa >= proximo_id:
            raise ErroAgenda("arquivo invalido")
        ids.add(id_tarefa)

        if (
            not isinstance(titulo, str)
            or titulo == ""
            or titulo != titulo.strip()
            or not _titulo_gravavel(titulo)
        ):
            raise ErroAgenda("arquivo invalido")
        if tarefa["prioridade"] not in PRIORIDADES:
            raise ErroAgenda("arquivo invalido")
        if prazo is not None and not _data_valida(prazo):
            raise ErroAgenda("arquivo invalido")
        if not isinstance(tarefa["concluida"], bool):
            raise ErroAgenda("arquivo invalido")


def carregar(caminho, criar_se_faltar=False):
    if not os.path.exists(caminho):
        if criar_se_faltar:
            return {"proximo_id": 1, "tarefas": []}
        raise ErroAgenda("arquivo inexistente")

    try:
        with open(caminho, "rb") as arquivo:
            texto = arquivo.read().decode("utf-8")
        dados = json.loads(
            texto,
            object_pairs_hook=_objeto_sem_chaves_repetidas,
            parse_constant=_recusar_constante,
        )
    except (OSError, ValueError):
        raise ErroAgenda("arquivo invalido")

    validar(dados)
    return dados


def salvar(caminho, dados):
    texto = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"
    try:
        with open(caminho, "w", encoding="utf-8", newline="") as arquivo:
            arquivo.write(texto)
    except (OSError, UnicodeEncodeError):
        raise ErroAgenda("nao foi possivel gravar arquivo")


def executar_adicionar(args):
    titulo = args.titulo.strip()
    if not titulo:
        raise ErroAgenda("titulo vazio")
    if not _titulo_gravavel(titulo):
        raise ErroAgenda("titulo invalido")
    if args.prazo is not None and not _data_valida(args.prazo):
        raise ErroAgenda("prazo invalido")

    dados = carregar(args.arquivo, criar_se_faltar=True)
    id_novo = dados["proximo_id"]
    dados["tarefas"].append(
        {
            "id": id_novo,
            "titulo": titulo,
            "prioridade": args.prioridade,
            "prazo": args.prazo,
            "concluida": False,
        }
    )
    dados["proximo_id"] = id_novo + 1
    salvar(args.arquivo, dados)
    return f"ok id={id_novo}\n"


def executar_listar(args):
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
        linhas.append(f"{t['id']}\t{t['prioridade']}\t{estado}\t{prazo}\t{t['titulo']}\n")
    return "".join(linhas)


def executar_concluir(args):
    dados = carregar(args.arquivo)
    tarefa = next((t for t in dados["tarefas"] if t["id"] == args.id), None)
    if tarefa is None:
        raise ErroAgenda("id inexistente")
    if tarefa["concluida"]:
        raise ErroAgenda("ja concluida")

    tarefa["concluida"] = True
    salvar(args.arquivo, dados)
    return f"ok id={args.id}\n"


def montar_parser():
    parser = argparse.ArgumentParser(description="Agenda pessoal em arquivo JSON.", allow_abbrev=False)
    subcomandos = parser.add_subparsers(dest="comando", metavar="{adicionar,listar,concluir}", required=True)

    adicionar = subcomandos.add_parser("adicionar", help="adiciona uma tarefa", allow_abbrev=False)
    adicionar.add_argument("--titulo", required=True)
    adicionar.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    adicionar.add_argument("--prazo")
    adicionar.add_argument("--arquivo", required=True)
    adicionar.set_defaults(executar=executar_adicionar)

    listar = subcomandos.add_parser("listar", help="lista tarefas", allow_abbrev=False)
    listar.add_argument("--prioridade", choices=PRIORIDADES)
    listar.add_argument("--somente-abertas", action="store_true")
    listar.add_argument("--arquivo", required=True)
    listar.set_defaults(executar=executar_listar)

    concluir = subcomandos.add_parser("concluir", help="marca uma tarefa como concluida", allow_abbrev=False)
    concluir.add_argument("--id", required=True, type=int)
    concluir.add_argument("--arquivo", required=True)
    concluir.set_defaults(executar=executar_concluir)

    return parser


def _escrever(fluxo, texto):
    fluxo.buffer.write(texto.encode("utf-8"))
    fluxo.buffer.flush()


def main(argv=None):
    args = montar_parser().parse_args(argv)
    try:
        saida = args.executar(args)
    except ErroAgenda as erro:
        _escrever(sys.stderr, f"erro: {erro}\n")
        return 2
    _escrever(sys.stdout, saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
