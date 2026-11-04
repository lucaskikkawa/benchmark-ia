#!/usr/bin/env python3
"""Contador de palavras pela linha de comando."""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter


def _inteiro_positivo(valor: str) -> int:
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(
            f"valor invalido: {valor!r} (esperado inteiro positivo)"
        ) from None
    if numero <= 0:
        raise argparse.ArgumentTypeError(
            f"valor invalido: {numero} (esperado inteiro positivo)"
        )
    return numero


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Conta palavras de um arquivo de texto UTF-8.",
        allow_abbrev=False,
    )
    parser.add_argument("arquivo", metavar="ARQUIVO", help="arquivo de texto UTF-8")
    parser.add_argument(
        "--minimo",
        type=_inteiro_positivo,
        default=1,
        help="exibe somente tokens com contagem maior ou igual a N (padrao: 1)",
    )
    parser.add_argument(
        "--top",
        type=_inteiro_positivo,
        default=None,
        help="limita a N resultados depois de ordenar",
    )
    parser.add_argument(
        "--ignorar-caixa",
        action="store_true",
        help="aplica str.casefold() antes de contar",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="escreve uma lista JSON de objetos palavra/contagem",
    )
    return parser


def _emitir(itens: list[tuple[str, int]], como_json: bool) -> None:
    if como_json:
        payload = [{"palavra": palavra, "contagem": contagem} for palavra, contagem in itens]
        sys.stdout.write(json.dumps(payload, ensure_ascii=False))
        sys.stdout.write("\n")
        return
    for palavra, contagem in itens:
        sys.stdout.write(f"{palavra}\t{contagem}\n")


def main(argv: list[str] | None = None) -> int:
    if argv is None:
        argv = sys.argv[1:]

    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        codigo = exc.code
        if codigo is None:
            return 0
        if isinstance(codigo, int):
            return codigo
        return 2

    try:
        with open(args.arquivo, encoding="utf-8") as arquivo:
            texto = arquivo.read()
    except UnicodeDecodeError:
        sys.stderr.write("erro: arquivo nao esta em UTF-8 valido\n")
        return 2
    except OSError:
        sys.stderr.write("erro: nao foi possivel ler o arquivo\n")
        return 2

    tokens = texto.split()
    if args.ignorar_caixa:
        tokens = [token.casefold() for token in tokens]

    contagens = Counter(tokens)
    itens = [
        (palavra, contagem)
        for palavra, contagem in contagens.items()
        if contagem >= args.minimo
    ]
    itens.sort(key=lambda item: (-item[1], item[0]))
    if args.top is not None:
        itens = itens[: args.top]

    _emitir(itens, args.json)
    return 0


if __name__ == "__main__":
    sys.exit(main())
