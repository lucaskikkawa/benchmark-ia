import argparse
import datetime
import json
import os
import re
import sys

PRIORIDADES = ("baixa", "media", "alta")
ORDEM_PRIORIDADE = {"alta": 0, "media": 1, "baixa": 2}
DATE_RE = re.compile(r"\A[0-9]{4}-[0-9]{2}-[0-9]{2}\Z")


def erro(msg: str) -> None:
    sys.stderr.write(f"erro: {msg}\n")
    sys.exit(2)


def validar_prazo(valor: str) -> bool:
    if type(valor) is not str or not DATE_RE.match(valor):
        return False
    ano = int(valor[0:4])
    mes = int(valor[5:7])
    dia = int(valor[8:10])
    try:
        datetime.date(ano, mes, dia)
    except ValueError:
        return False
    return True


def _sem_chaves_duplicadas(pares):
    obj = {}
    for k, v in pares:
        if k in obj:
            raise ValueError("chave duplicada")
        obj[k] = v
    return obj


def validar_dados(dados) -> bool:
    if type(dados) is not dict:
        return False
    if set(dados.keys()) != {"proximo_id", "tarefas"}:
        return False

    proximo_id = dados["proximo_id"]
    tarefas = dados["tarefas"]

    if type(proximo_id) is not int or proximo_id < 1:
        return False
    if type(tarefas) is not list:
        return False

    ids_vistos = set()
    chaves_esperadas = {"id", "titulo", "prioridade", "prazo", "concluida"}

    for t in tarefas:
        if type(t) is not dict:
            return False
        if set(t.keys()) != chaves_esperadas:
            return False

        tid = t["id"]
        titulo = t["titulo"]
        prioridade = t["prioridade"]
        prazo = t["prazo"]
        concluida = t["concluida"]

        if type(tid) is not int or tid < 1 or tid >= proximo_id or tid in ids_vistos:
            return False
        ids_vistos.add(tid)

        if type(titulo) is not str or len(titulo) == 0:
            return False
        if titulo != titulo.strip():
            return False
        if "\n" in titulo or "\r" in titulo or "\t" in titulo:
            return False

        if type(prioridade) is not str or prioridade not in PRIORIDADES:
            return False

        if prazo is not None and not validar_prazo(prazo):
            return False

        if type(concluida) is not bool:
            return False

    return True


def ler_arquivo(caminho: str, exigir_existente: bool):
    if not os.path.lexists(caminho):
        if exigir_existente:
            erro("arquivo inexistente")
        return {"proximo_id": 1, "tarefas": []}

    if os.path.isdir(caminho):
        erro("arquivo invalido")

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
        dados = json.loads(conteudo, object_pairs_hook=_sem_chaves_duplicadas)
    except Exception:
        erro("arquivo invalido")

    if not validar_dados(dados):
        erro("arquivo invalido")

    return dados


def salvar_arquivo(caminho: str, dados: dict) -> None:
    tarefas_ordenadas_chaves = [
        {
            "id": t["id"],
            "titulo": t["titulo"],
            "prioridade": t["prioridade"],
            "prazo": t["prazo"],
            "concluida": t["concluida"],
        }
        for t in dados["tarefas"]
    ]
    saida = {
        "proximo_id": dados["proximo_id"],
        "tarefas": tarefas_ordenadas_chaves,
    }
    texto = json.dumps(saida, indent=2, ensure_ascii=False) + "\n"
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)


def cmd_adicionar(args) -> None:
    # Se o arquivo já existe, valida antes para garantir erro: arquivo invalido
    # se for inválido (e não alterar o arquivo de forma alguma).
    dados = None
    if os.path.lexists(args.arquivo):
        dados = ler_arquivo(args.arquivo, exigir_existente=True)

    titulo = args.titulo.strip()
    if not titulo:
        erro("titulo vazio")
    if "\n" in titulo or "\r" in titulo or "\t" in titulo:
        erro("titulo invalido")

    prazo = args.prazo
    if prazo is not None and not validar_prazo(prazo):
        erro("prazo invalido")

    if dados is None:
        dados = {"proximo_id": 1, "tarefas": []}

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

    salvar_arquivo(args.arquivo, dados)
    sys.stdout.write(f"ok id={novo_id}\n")


def cmd_listar(args) -> None:
    dados = ler_arquivo(args.arquivo, exigir_existente=True)
    tarefas = dados["tarefas"]

    if args.prioridade is not None:
        tarefas = [t for t in tarefas if t["prioridade"] == args.prioridade]
    if args.somente_abertas:
        tarefas = [t for t in tarefas if not t["concluida"]]

    tarefas.sort(key=lambda t: (ORDEM_PRIORIDADE[t["prioridade"]], t["id"]))

    linhas = []
    for t in tarefas:
        estado = "concluida" if t["concluida"] else "aberta"
        prazo = "-" if t["prazo"] is None else t["prazo"]
        linhas.append(f"{t['id']}\t{t['prioridade']}\t{estado}\t{prazo}\t{t['titulo']}\n")

    if linhas:
        sys.stdout.write("".join(linhas))


def cmd_concluir(args) -> None:
    dados = ler_arquivo(args.arquivo, exigir_existente=True)
    alvo = None
    for t in dados["tarefas"]:
        if t["id"] == args.id:
            alvo = t
            break

    if alvo is None:
        erro("id inexistente")
    if alvo["concluida"]:
        erro("ja concluida")

    alvo["concluida"] = True
    salvar_arquivo(args.arquivo, dados)
    sys.stdout.write(f"ok id={alvo['id']}\n")


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agenda_cli.py", allow_abbrev=False)
    subparsers = parser.add_subparsers(dest="subcomando", required=True)

    p_add = subparsers.add_parser("adicionar", allow_abbrev=False)
    p_add.add_argument("--titulo", required=True, type=str)
    p_add.add_argument("--prioridade", required=True, choices=PRIORIDADES)
    p_add.add_argument("--prazo", required=False, default=None, type=str)
    p_add.add_argument("--arquivo", required=True, type=str)
    p_add.set_defaults(func=cmd_adicionar)

    p_list = subparsers.add_parser("listar", allow_abbrev=False)
    p_list.add_argument("--arquivo", required=True, type=str)
    p_list.add_argument("--prioridade", required=False, default=None, choices=PRIORIDADES)
    p_list.add_argument("--somente-abertas", action="store_true")
    p_list.set_defaults(func=cmd_listar)

    p_done = subparsers.add_parser("concluir", allow_abbrev=False)
    p_done.add_argument("--id", required=True, type=int)
    p_done.add_argument("--arquivo", required=True, type=str)
    p_done.set_defaults(func=cmd_concluir)

    return parser


def main() -> None:
    parser = criar_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
