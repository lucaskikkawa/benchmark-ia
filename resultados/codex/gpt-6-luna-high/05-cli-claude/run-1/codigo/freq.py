#!/usr/bin/env python3
"""Count the most frequent Unicode words in a UTF-8 text file."""

import argparse
import json
import re
import sys
from collections import Counter


WORD_RE = re.compile(r"[^\W\d_]+")


def positive_int(value: str) -> int:
    try:
        number = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("deve ser um inteiro >= 1") from exc
    if number < 1:
        raise argparse.ArgumentTypeError("deve ser um inteiro >= 1")
    return number


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Conta as palavras mais frequentes de um arquivo UTF-8.")
    parser.add_argument("arquivo", help="arquivo de texto UTF-8; use - para ler da entrada padrão")
    parser.add_argument("-n", "--top", type=positive_int, default=10, metavar="N",
                        help="quantas palavras mostrar (padrão: 10)")
    parser.add_argument("-m", "--min-len", type=positive_int, default=1, metavar="K",
                        help="ignora palavras menores que K caracteres (padrão: 1)")
    parser.add_argument("-i", "--ignore-case", action="store_true",
                        help="converte palavras para minúsculas antes de contar")
    parser.add_argument("-x", "--excluir", action="append", default=[], metavar="PALAVRA",
                        help="ignora PALAVRA; pode ser repetido")
    parser.add_argument("--formato", choices=("texto", "json"), default="texto",
                        help="formato de saída (padrão: texto)")
    return parser


def read_input(path: str) -> str:
    if path == "-":
        data = sys.stdin.buffer.read()
    else:
        with open(path, "rb") as source:
            data = source.read()
    return data.decode("utf-8", errors="strict")


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()

    try:
        text = read_input(args.arquivo)
    except (OSError, UnicodeDecodeError) as exc:
        message = str(exc).replace("\r", " ").replace("\n", " ")
        sys.stderr.write(f"erro: {message}\n")
        return 1

    excluded = {word.lower() if args.ignore_case else word for word in args.excluir}
    counts = Counter()
    for word in WORD_RE.findall(text):
        if args.ignore_case:
            word = word.lower()
        if len(word) >= args.min_len and word not in excluded:
            counts[word] += 1

    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[:args.top]
    if args.formato == "json":
        output = json.dumps(
            [{"palavra": word, "contagem": count} for word, count in ranked],
            ensure_ascii=False,
        )
    else:
        output = "".join(f"{word}\t{count}\n" for word, count in ranked)

    # Write UTF-8 bytes directly so output behavior does not depend on the locale.
    sys.stdout.buffer.write(output.encode("utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
