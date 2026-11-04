#!/usr/bin/env python3
"""Conta e exibe as palavras mais frequentes de um arquivo de texto."""

import argparse
from collections import Counter
import json
import re
import sys


WORD_RE = re.compile(r"[^\W\d_]+")


def positive_int(value):
    try:
        number = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} não é um inteiro")
    if number < 1:
        raise argparse.ArgumentTypeError("o valor deve ser >= 1")
    return number


def make_parser():
    parser = argparse.ArgumentParser(description="Conta as palavras mais frequentes de um arquivo.")
    parser.add_argument("arquivo", help="arquivo de texto UTF-8; use - para ler da entrada padrão")
    parser.add_argument("-n", "--top", type=positive_int, default=10, metavar="N",
                        help="quantas palavras mostrar (padrão: 10)")
    parser.add_argument("-m", "--min-len", type=positive_int, default=1, metavar="K",
                        help="comprimento mínimo das palavras (padrão: 1)")
    parser.add_argument("-i", "--ignore-case", action="store_true",
                        help="converte palavras para minúsculas antes de contar")
    parser.add_argument("-x", "--excluir", action="append", default=[], metavar="PALAVRA",
                        help="palavra a ignorar (pode ser repetida)")
    parser.add_argument("--formato", choices=("texto", "json"), default="texto",
                        help="formato de saída (padrão: texto)")
    return parser


def read_input(path):
    if path == "-":
        data = sys.stdin.buffer.read()
    else:
        with open(path, "rb") as source:
            data = source.read()
    return data.decode("utf-8", errors="strict")


def main(argv=None):
    args = make_parser().parse_args(argv)
    try:
        content = read_input(args.arquivo)
    except (OSError, UnicodeDecodeError) as exc:
        message = str(exc).splitlines()[0] if str(exc) else exc.__class__.__name__
        print(f"erro: {message}", file=sys.stderr)
        return 1

    excluded = {word.lower() if args.ignore_case else word for word in args.excluir}
    words = Counter()
    for word in WORD_RE.findall(content):
        if args.ignore_case:
            word = word.lower()
        if len(word) < args.min_len or word in excluded:
            continue
        words[word] += 1

    results = sorted(words.items(), key=lambda item: (-item[1], item[0]))[:args.top]
    if args.formato == "json":
        output = json.dumps(
            [{"palavra": word, "contagem": count} for word, count in results],
            ensure_ascii=False,
        )
        print(output)
    else:
        for word, count in results:
            print(f"{word}\t{count}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
