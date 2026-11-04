#!/usr/bin/env python3
"""Contador de palavras pela linha de comando."""

import argparse
import json
import re
import sys
from collections import Counter


def _inteiro_positivo(valor):
    if not re.fullmatch(r"\+?[0-9]+", valor) or int(valor) <= 0:
        raise argparse.ArgumentTypeError(f"esperado inteiro positivo, recebido {valor!r}")
    return int(valor)


def _criar_parser():
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Conta as palavras de um arquivo UTF-8.",
        allow_abbrev=False,
    )
    parser.add_argument("arquivo", metavar="ARQUIVO", help="arquivo UTF-8 a ser lido")
    parser.add_argument(
        "--minimo",
        type=_inteiro_positivo,
        default=1,
        metavar="N",
        help="exibe apenas tokens com contagem >= N (padrão: 1)",
    )
    parser.add_argument(
        "--top",
        type=_inteiro_positivo,
        default=None,
        metavar="N",
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
        help="escreve uma lista JSON de objetos {'palavra', 'contagem'}",
    )
    return parser


def _contar(texto, ignorar_caixa):
    tokens = texto.split()
    if ignorar_caixa:
        tokens = [token.casefold() for token in tokens]
    return Counter(tokens)


def _ranquear(contagem, minimo, top):
    itens = [(palavra, n) for palavra, n in contagem.items() if n >= minimo]
    itens.sort(key=lambda item: (-item[1], item[0]))
    if top is not None:
        itens = itens[:top]
    return itens


def main(argv=None):
    try:
        args = _criar_parser().parse_args(argv)
    except SystemExit as erro:
        return erro.code if isinstance(erro.code, int) else 0

    try:
        with open(args.arquivo, "rb") as arquivo:
            texto = arquivo.read().decode("utf-8")
    except UnicodeDecodeError:
        print(f"cli.py: erro: {args.arquivo!r} não é UTF-8 válido", file=sys.stderr)
        return 2
    except OSError as erro:
        motivo = erro.strerror or str(erro)
        print(f"cli.py: erro: não foi possível ler {args.arquivo!r}: {motivo}", file=sys.stderr)
        return 2

    itens = _ranquear(_contar(texto, args.ignorar_caixa), args.minimo, args.top)

    if args.json:
        dados = [{"palavra": palavra, "contagem": n} for palavra, n in itens]
        sys.stdout.write(json.dumps(dados, ensure_ascii=False) + "\n")
    else:
        sys.stdout.write("".join(f"{palavra}\t{n}\n" for palavra, n in itens))
    return 0


if __name__ == "__main__":
    sys.exit(main())
