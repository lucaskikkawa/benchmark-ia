#!/usr/bin/env python3
"""Conta métricas básicas de um arquivo de texto UTF-8."""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys


PONTUACAO_PONTAS = '.,!?;:"\'()[]{}'


def inteiro_positivo(valor: str) -> int:
    try:
        numero = int(valor)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("deve ser um inteiro maior ou igual a 1") from exc
    if numero < 1:
        raise argparse.ArgumentTypeError("deve ser um inteiro maior ou igual a 1")
    return numero


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Conta métricas de um arquivo de texto.")
    parser.add_argument("arquivo", help="caminho para o arquivo de texto UTF-8")
    parser.add_argument("-l", "--linhas", action="store_true", help="conta as linhas")
    parser.add_argument("-p", "--palavras", action="store_true", help="conta as palavras")
    parser.add_argument("-c", "--chars", action="store_true", help="conta os caracteres")
    parser.add_argument("--top", type=inteiro_positivo, metavar="N", help="exibe as N palavras mais frequentes")
    parser.add_argument("--json", action="store_true", help="formata a saída como JSON")
    parser.add_argument("-o", "--saida", metavar="CAMINHO", help="grava a saída em um arquivo")
    return parser


def montar_resultado(conteudo: str, args: argparse.Namespace) -> dict:
    selecionou_metrica = args.linhas or args.palavras or args.chars or args.top is not None
    incluir_linhas = args.linhas or not selecionou_metrica
    incluir_palavras = args.palavras or not selecionou_metrica
    incluir_chars = args.chars or not selecionou_metrica

    resultado = {}
    if incluir_linhas:
        resultado["linhas"] = len(conteudo.splitlines())
    if incluir_palavras:
        resultado["palavras"] = len(conteudo.split())
    if incluir_chars:
        resultado["caracteres"] = len(conteudo)
    if args.top is not None:
        tokens = (token.lower().strip(PONTUACAO_PONTAS) for token in conteudo.split())
        frequencias = Counter(token for token in tokens if token)
        ordenadas = sorted(frequencias.items(), key=lambda item: (-item[1], item[0]))
        resultado["top_palavras"] = [
            {"palavra": palavra, "ocorrencias": ocorrencias}
            for palavra, ocorrencias in ordenadas[: args.top]
        ]
    return resultado


def formatar_texto(resultado: dict) -> str:
    rotulos = {
        "linhas": "Linhas",
        "palavras": "Palavras",
        "caracteres": "Caracteres",
    }
    linhas = []
    for chave, rotulo in rotulos.items():
        if chave in resultado:
            linhas.append(f"{rotulo}: {resultado[chave]}")
    if "top_palavras" in resultado:
        linhas.append("Top Palavras:")
        linhas.extend(
            f"  - {item['palavra']}: {item['ocorrencias']}"
            for item in resultado["top_palavras"]
        )
    return "\n".join(linhas) + "\n"


def main() -> int:
    parser = criar_parser()
    args = parser.parse_args()

    caminho = Path(args.arquivo)
    try:
        if not caminho.is_file():
            raise OSError("o caminho não aponta para um arquivo regular")
        conteudo = caminho.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        print(f"Erro ao ler arquivo: {exc}", file=sys.stderr)
        return 1

    resultado = montar_resultado(conteudo, args)
    saida = (
        json.dumps(resultado, indent=2, ensure_ascii=False) + "\n"
        if args.json
        else formatar_texto(resultado)
    )

    if args.saida is not None:
        destino = Path(args.saida)
        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(saida, encoding="utf-8")
        except OSError as exc:
            print(f"Erro ao gravar arquivo: {exc}", file=sys.stderr)
            return 1
        print(f"Salvo em {args.saida}")
    else:
        sys.stdout.write(saida)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
