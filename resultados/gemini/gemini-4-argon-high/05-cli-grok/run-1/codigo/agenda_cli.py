import argparse
import datetime
import json
import os
import re
import sys

PRIORIDADES_VALIDAS = ("baixa", "media", "alta")
ORDEM_PRIORIDADE = {"alta": 0, "media": 1, "baixa": 2}
CHAVES_RAIZ = {"proximo_id", "tarefas"}
CHAVES_TAREFA = {"id", "titulo", "prioridade", "prazo", "concluida"}
REGEX_DATA = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


def erro(mensagem: str) -> None:
    sys.stderr.write(f"erro: {mensagem}\n")
    sys.exit(2)


def data_valida(valor: object) -> bool:
    if type(valor) is not str:
        return False
    if not REGEX_DATA.fullmatch(valor):
        return False
    ano = int(valor[0:4])
    mes = int(valor[5:7])
    dia = int(valor[8:10])
    try:
        datetime.date(ano, mes, dia)
    except ValueError:
        return False
    return True


def titulo_armazenado_valido(valor: object) -> bool:
    if type(valor) is not str:
        return False
    if valor == "":
        return False
    if valor != valor.strip():
        return False
    if "\n" in valor or "\r" in valor or "\t" in valor:
        return False
    return True


def _pares_sem_duplicatas(pares: list[tuple[str, object]]) -> dict[str, object]:
    obj: dict[str, object] = {}
    for chave, valor in pares:
        if chave in obj:
            raise ValueError("chave duplicada")
        obj[chave] = valor
    return obj


def _constante_invalida(_valor: str) -> None:
    raise ValueError("constante JSON invalida")


def validar_estrutura_agenda(dados: object) -> tuple[int, list[dict[str, object]]]:
    if type(dados) is not dict:
        erro("arquivo invalido")
    if set(dados.keys()) != CHAVES_RAIZ:
        erro("arquivo invalido")

    proximo_id = dados["proximo_id"]
    tarefas = dados["tarefas"]

    if type(proximo_id) is not int or proximo_id < 1:
        erro("arquivo invalido")
    if type(tarefas) is not list:
        erro("arquivo invalido")

    ids_vistos: set[int] = set()
    for tarefa in tarefas:
        if type(tarefa) is not dict:
            erro("arquivo invalido")
        if set(tarefa.keys()) != CHAVES_TAREFA:
            erro("arquivo invalido")

        tid = tarefa["id"]
        titulo = tarefa["titulo"]
        prioridade = tarefa["prioridade"]
        prazo = tarefa["prazo"]
        concluida = tarefa["concluida"]

        if type(tid) is not int or tid < 1:
            erro("arquivo invalido")
        if tid in ids_vistos:
            erro("arquivo invalido")
        if proximo_id <= tid:
            erro("arquivo invalido")
        ids_vistos.add(tid)

        if not titulo_armazenado_valido(titulo):
            erro("arquivo invalido")

        if type(prioridade) is not str or prioridade not in PRIORIDADES_VALIDAS:
            erro("arquivo invalido")

        if prazo is not None and not data_valida(prazo):
            erro("arquivo invalido")

        if type(concluida) is not bool:
            erro("arquivo invalido")

    return proximo_id, tarefas


def carregar_agenda(caminho: str, permitir_inexistente: bool = False) -> tuple[int, list[dict[str, object]]]:
    if not os.path.lexists(caminho):
        if permitir_inexistente:
            return 1, []
        erro("arquivo inexistente")

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except FileNotFoundError:
        if permitir_inexistente:
            return 1, []
        erro("arquivo inexistente")
    except OSError:
        erro("arquivo invalido")
    except UnicodeDecodeError:
        erro("arquivo invalido")

    try:
        dados = json.loads(
            conteudo,
            object_pairs_hook=_pares_sem_duplicatas,
            parse_constant=_constante_invalida,
        )
    except (json.JSONDecodeError, ValueError):
        erro("arquivo invalido")

    return validar_estrutura_agenda(dados)


def salvar_agenda(caminho: str, proximo_id: int, tarefas: list[dict[str, object]]) -> None:
    dados = {
        "proximo_id": proximo_id,
        "tarefas": [
            {
                "id": t["id"],
                "titulo": t["titulo"],
                "prioridade": t["prioridade"],
                "prazo": t["prazo"],
                "concluida": t["concluida"],
            }
            for t in tarefas
        ],
    }
    texto = json.dumps(dados, indent=2, ensure_ascii=False) + "\n"
    with open(caminho, "w", encoding="utf-8", newline="\n") as f:
        f.write(texto)


def cmd_adicionar(args: argparse.Namespace) -> None:
    titulo = args.titulo.strip()
    if titulo == "":
        erro("titulo vazio")
    if "\n" in titulo or "\r" in titulo or "\t" in titulo:
        erro("titulo invalido")

    prazo = args.prazo
    if prazo is not None and not data_valida(prazo):
        erro("prazo invalido")

    proximo_id, tarefas = carregar_agenda(args.arquivo, permitir_inexistente=True)

    novo_id = proximo_id
    tarefas.append(
        {
            "id": novo_id,
            "titulo": titulo,
            "prioridade": args.prioridade,
            "prazo": prazo,
            "concluida": False,
        }
    )
    salvar_agenda(args.arquivo, proximo_id + 1, tarefas)
    sys.stdout.write(f"ok id={novo_id}\n")


def cmd_listar(args: argparse.Namespace) -> None:
    _proximo_id, tarefas = carregar_agenda(args.arquivo, permitir_inexistente=False)

    filtradas = []
    for t in tarefas:
        if args.prioridade is not None and t["prioridade"] != args.prioridade:
            continue
        if args.somente_abertas and t["concluida"]:
            continue
        filtradas.append(t)

    filtradas.sort(key=lambda t: (ORDEM_PRIORIDADE[str(t["prioridade"])], int(t["id"])))

    for t in filtradas:
        estado = "concluida" if t["concluida"] else "aberta"
        prazo = "-" if t["prazo"] is None else str(t["prazo"])
        sys.stdout.write(f"{t['id']}\t{t['prioridade']}\t{estado}\t{prazo}\t{t['titulo']}\n")


def cmd_concluir(args: argparse.Namespace) -> None:
    proximo_id, tarefas = carregar_agenda(args.arquivo, permitir_inexistente=False)

    alvo = None
    for t in tarefas:
        if t["id"] == args.id:
            alvo = t
            break

    if alvo is None:
        erro("id inexistente")

    if alvo["concluida"]:
        erro("ja concluida")

    alvo["concluida"] = True
    salvar_agenda(args.arquivo, proximo_id, tarefas)
    sys.stdout.write(f"ok id={alvo['id']}\n")


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agenda_cli.py")
    subparsers = parser.add_subparsers(dest="subcomando", required=True)

    p_add = subparsers.add_parser("adicionar")
    p_add.add_argument("--titulo", required=True)
    p_add.add_argument("--prioridade", required=True, choices=PRIORIDADES_VALIDAS)
    p_add.add_argument("--prazo", required=False, default=None)
    p_add.add_argument("--arquivo", required=True)

    p_list = subparsers.add_parser("listar")
    p_list.add_argument("--arquivo", required=True)
    p_list.add_argument("--prioridade", required=False, default=None, choices=PRIORIDADES_VALIDAS)
    p_list.add_argument("--somente-abertas", action="store_true")

    p_done = subparsers.add_parser("concluir")
    p_done.add_argument("--id", required=True, type=int)
    p_done.add_argument("--arquivo", required=True)

    return parser


def main() -> None:
    parser = construir_parser()
    args = parser.parse_args()

    if args.subcomando == "adicionar":
        cmd_adicionar(args)
    elif args.subcomando == "listar":
        cmd_listar(args)
    elif args.subcomando == "concluir":
        cmd_concluir(args)


if __name__ == "__main__":
    main()
