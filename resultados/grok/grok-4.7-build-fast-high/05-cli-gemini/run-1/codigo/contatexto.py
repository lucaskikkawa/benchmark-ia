#!/usr/bin/env python3
"""Ferramenta CLI de contagem e métricas de texto."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

PONTUACAO = ".,!?;:\"'()[]{}"


def inteiro_positivo(valor: str) -> int:
    try:
        numero = int(valor)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"valor inválido para --top: {valor!r}"
        ) from exc
    if numero < 1:
        raise argparse.ArgumentTypeError("--top requer um inteiro >= 1")
    return numero


def construir_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Contagem e métricas de texto."
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="caminho para o arquivo de texto UTF-8 a ser analisado",
    )
    parser.add_argument(
        "-l",
        "--linhas",
        action="store_true",
        help="contabiliza a quantidade de linhas",
    )
    parser.add_argument(
        "-p",
        "--palavras",
        action="store_true",
        help="contabiliza o total de palavras",
    )
    parser.add_argument(
        "-c",
        "--chars",
        action="store_true",
        help="contabiliza o total de caracteres",
    )
    parser.add_argument(
        "--top",
        type=inteiro_positivo,
        metavar="N",
        help="lista as N palavras mais frequentes",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="formata o resultado como um objeto JSON",
    )
    parser.add_argument(
        "-o",
        "--saida",
        metavar="CAMINHO",
        help="grava a saída no caminho especificado",
    )
    return parser


def ler_conteudo(caminho: str) -> str:
    origem = Path(caminho)
    if not origem.exists():
        print(f"Erro: arquivo não encontrado: {caminho}", file=sys.stderr)
        sys.exit(1)
    if origem.is_dir():
        print(
            f"Erro: caminho aponta para um diretório em vez de arquivo regular: {caminho}",
            file=sys.stderr,
        )
        sys.exit(1)
    if not origem.is_file():
        print(f"Erro: caminho não é um arquivo regular: {caminho}", file=sys.stderr)
        sys.exit(1)
    try:
        return origem.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        print(f"Erro ao ler arquivo: {exc}", file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Erro ao ler arquivo: {exc}", file=sys.stderr)
        sys.exit(1)


def calcular_top(conteudo: str, limite: int) -> list[dict[str, int | str]]:
    contagem: Counter[str] = Counter()
    for token in conteudo.split():
        palavra = token.lower().strip(PONTUACAO)
        if palavra:
            contagem[palavra] += 1
    ordenadas = sorted(contagem.items(), key=lambda item: (-item[1], item[0]))
    return [
        {"palavra": palavra, "ocorrencias": ocorrencias}
        for palavra, ocorrencias in ordenadas[:limite]
    ]


def montar_metricas(conteudo: str, args: argparse.Namespace) -> dict:
    selecionou = bool(args.linhas or args.palavras or args.chars or args.top is not None)
    metricas: dict = {}
    if not selecionou or args.linhas:
        metricas["linhas"] = len(conteudo.splitlines())
    if not selecionou or args.palavras:
        metricas["palavras"] = len(conteudo.split())
    if not selecionou or args.chars:
        metricas["caracteres"] = len(conteudo)
    if args.top is not None:
        metricas["top_palavras"] = calcular_top(conteudo, args.top)
    return metricas


def formatar_texto(metricas: dict) -> str:
    linhas_saida: list[str] = []
    if "linhas" in metricas:
        linhas_saida.append(f"Linhas: {metricas['linhas']}")
    if "palavras" in metricas:
        linhas_saida.append(f"Palavras: {metricas['palavras']}")
    if "caracteres" in metricas:
        linhas_saida.append(f"Caracteres: {metricas['caracteres']}")
    if "top_palavras" in metricas:
        linhas_saida.append("Top Palavras:")
        for item in metricas["top_palavras"]:
            linhas_saida.append(f"  - {item['palavra']}: {item['ocorrencias']}")
    if not linhas_saida:
        return ""
    return "\n".join(linhas_saida) + "\n"


def formatar_json(metricas: dict) -> str:
    return json.dumps(metricas, indent=2, ensure_ascii=False) + "\n"


def gravar_saida(caminho: str, conteudo: str) -> None:
    destino = Path(caminho)
    try:
        if destino.parent != Path(""):
            destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(conteudo, encoding="utf-8")
    except OSError as exc:
        print(f"Erro ao gravar arquivo: {exc}", file=sys.stderr)
        sys.exit(1)


def main(argv: list[str] | None = None) -> None:
    parser = construir_parser()
    args = parser.parse_args(argv)
    conteudo = ler_conteudo(args.arquivo)
    metricas = montar_metricas(conteudo, args)
    resultado = formatar_json(metricas) if args.json else formatar_texto(metricas)
    if args.saida:
        gravar_saida(args.saida, resultado)
        print(f"Salvo em {args.saida}")
        return
    sys.stdout.write(resultado)


if __name__ == "__main__":
    main()
