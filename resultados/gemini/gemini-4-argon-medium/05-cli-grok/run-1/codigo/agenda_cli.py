import argparse
import datetime
import json
import os
import sys


def erro(msg: str) -> None:
    sys.stderr.write(f"erro: {msg}\n")
    sys.exit(2)


def validar_prazo(valor: object) -> bool:
    if type(valor) is not str:
        return False
    if len(valor) != 10 or valor[4] != "-" or valor[7] != "-":
        return False
    ano_s, mes_s, dia_s = valor[0:4], valor[5:7], valor[8:10]
    if not (
        ano_s.isascii()
        and ano_s.isdigit()
        and mes_s.isascii()
        and mes_s.isdigit()
        and dia_s.isascii()
        and dia_s.isdigit()
    ):
        return False
    try:
        datetime.date(int(ano_s), int(mes_s), int(dia_s))
    except ValueError:
        return False
    return True


def _sem_chaves_duplicadas(pares: list[tuple[str, object]]) -> dict[str, object]:
    obj: dict[str, object] = {}
    for k, v in pares:
        if k in obj:
            raise ValueError("chave duplicada")
        obj[k] = v
    return obj


def validar_dados(dados: object) -> dict[str, object]:
    if type(dados) is not dict:
        erro("arquivo invalido")
    if set(dados.keys()) != {"proximo_id", "tarefas"}:
        erro("arquivo invalido")

    proximo_id = dados["proximo_id"]
    tarefas = dados["tarefas"]

    if type(proximo_id) is not int or proximo_id < 1:
        erro("arquivo invalido")
    if type(tarefas) is not list:
        erro("arquivo invalido")

    ids_vistos: set[int] = set()
    tarefas_normalizadas: list[dict[str, object]] = []
    chaves_esperadas = {"id", "titulo", "prioridade", "prazo", "concluida"}

    for t in tarefas:
        if type(t) is not dict:
            erro("arquivo invalido")
        if set(t.keys()) != chaves_esperadas:
            erro("arquivo invalido")

        tid = t["id"]
        titulo = t["titulo"]
        prioridade = t["prioridade"]
        prazo = t["prazo"]
        concluida = t["concluida"]

        if type(tid) is not int or tid < 1 or tid in ids_vistos:
            erro("arquivo invalido")
        ids_vistos.add(tid)

        if type(titulo) is not str:
            erro("arquivo invalido")
        if not titulo or titulo != titulo.strip():
            erro("arquivo invalido")
        if "\n" in titulo or "\r" in titulo or "\t" in titulo:
            erro("arquivo invalido")

        if type(prioridade) is not str or prioridade not in ("baixa", "media", "alta"):
            erro("arquivo invalido")

        if prazo is not None and not validar_prazo(prazo):
            erro("arquivo invalido")

        if type(concluida) is not bool:
            erro("arquivo invalido")

        tarefas_normalizadas.append(
            {
                "id": tid,
                "titulo": titulo,
                "prioridade": prioridade,
                "prazo": prazo,
                "concluida": concluida,
            }
        )

    if ids_vistos and proximo_id <= max(ids_vistos):
        erro("arquivo invalido")

    return {
        "proximo_id": proximo_id,
        "tarefas": tarefas_normalizadas,
    }


def carregar_arquivo(caminho: str, obrigatorio: bool) -> dict[str, object]:
    if not os.path.exists(caminho):
        if obrigatorio:
            erro("arquivo inexistente")
        return {"proximo_id": 1, "tarefas": []}

    if not os.path.isfile(caminho):
        erro("arquivo invalido")

    try:
        with open(caminho, "r", encoding="utf-8") as f:
            conteudo = f.read()
        dados = json.loads(conteudo, object_pairs_hook=_sem_chaves_duplicadas)
    except Exception:
        erro("arquivo invalido")

    return validar_dados(dados)


def salvar_arquivo(caminho: str, dados: dict[str, object]) -> None:
    parent = os.path.dirname(caminho)
    if parent:
        os.makedirs(parent, exist_ok=True)
    saida = {
        "proximo_id": dados["proximo_id"],
        "tarefas": [
            {
                "id": t["id"],
                "titulo": t["titulo"],
                "prioridade": t["prioridade"],
                "prazo": t["prazo"],
                "concluida": t["concluida"],
            }
            for t in dados["tarefas"]
        ],
    }
    texto = json.dumps(saida, indent=2, ensure_ascii=False) + "\n"
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)


def cmd_adicionar(args: argparse.Namespace) -> None:
    dados = carregar_arquivo(args.arquivo, obrigatorio=False)

    titulo = args.titulo.strip()
    if not titulo:
        erro("titulo vazio")
    if "\n" in titulo or "\r" in titulo or "\t" in titulo:
        erro("titulo invalido")

    prazo = args.prazo
    if prazo is not None and not validar_prazo(prazo):
        erro("prazo invalido")

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
    dados = carregar_arquivo(args.arquivo, obrigatorio=True)
    tarefas = dados["tarefas"]

    if args.prioridade is not None:
        tarefas = [t for t in tarefas if t["prioridade"] == args.prioridade]
    if args.somente_abertas:
        tarefas = [t for t in tarefas if not t["concluida"]]

    ordem_prioridade = {"alta": 0, "media": 1, "baixa": 2}
    tarefas_ordenadas = sorted(
        tarefas,
        key=lambda t: (ordem_prioridade[t["prioridade"]], t["id"]),
    )

    for t in tarefas_ordenadas:
        estado = "concluida" if t["concluida"] else "aberta"
        prazo = t["prazo"] if t["prazo"] is not None else "-"
        sys.stdout.write(
            f"{t['id']}\t{t['prioridade']}\t{estado}\t{prazo}\t{t['titulo']}\n"
        )


def cmd_concluir(args: argparse.Namespace) -> None:
    dados = carregar_arquivo(args.arquivo, obrigatorio=True)
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


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="agenda_cli.py")
    subparsers = parser.add_subparsers(dest="subcomando", required=True)

    p_add = subparsers.add_parser("adicionar")
    p_add.add_argument("--titulo", required=True)
    p_add.add_argument(
        "--prioridade", required=True, choices=["baixa", "media", "alta"]
    )
    p_add.add_argument("--prazo", default=None)
    p_add.add_argument("--arquivo", required=True)
    p_add.set_defaults(func=cmd_adicionar)

    p_list = subparsers.add_parser("listar")
    p_list.add_argument("--arquivo", required=True)
    p_list.add_argument("--prioridade", default=None, choices=["baixa", "media", "alta"])
    p_list.add_argument("--somente-abertas", action="store_true")
    p_list.set_defaults(func=cmd_listar)

    p_done = subparsers.add_parser("concluir")
    p_done.add_argument("--id", required=True, type=int)
    p_done.add_argument("--arquivo", required=True)
    p_done.set_defaults(func=cmd_done_wrapper)

    return parser


def cmd_done_wrapper(args: argparse.Namespace) -> None:
    cmd_concluir(args)


def main() -> None:
    parser = construir_parser()
    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
