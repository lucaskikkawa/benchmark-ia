#!/usr/bin/env python3
"""CLI de frequência de palavras."""

from __future__ import annotations

import argparse
from collections import Counter
import heapq
import json
import re
import sys

WORD_RE = re.compile(r"[^\W\d_]+")


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"valor inteiro inválido: {value!r}"
        ) from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError(
            f"o valor deve ser um inteiro >= 1 (recebido: {parsed})"
        )
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="freq.py",
        description="Conta as palavras de um arquivo de texto e imprime as mais frequentes.",
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="caminho do arquivo de texto (UTF-8), ou '-' para entrada padrão",
    )
    parser.add_argument(
        "-n",
        "--top",
        type=positive_int,
        default=10,
        metavar="N",
        help="quantas palavras mostrar (inteiro >= 1; padrão: 10)",
    )
    parser.add_argument(
        "-m",
        "--min-len",
        type=positive_int,
        default=1,
        metavar="K",
        help="ignora palavras com menos de K caracteres (inteiro >= 1; padrão: 1)",
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="converte as palavras para minúsculas antes de contar",
    )
    parser.add_argument(
        "-x",
        "--excluir",
        action="append",
        default=[],
        metavar="PALAVRA",
        help="ignora essa palavra (pode ser repetida)",
    )
    parser.add_argument(
        "--formato",
        choices=("texto", "json"),
        default="texto",
        help="formato de saída (padrão: texto)",
    )
    return parser


def read_input(path: str) -> str:
    if path == "-":
        raw = sys.stdin.buffer.read()
    else:
        with open(path, "rb") as f:
            raw = f.read()
    return raw.decode("utf-8", errors="strict")


def count_words(
    text: str,
    *,
    ignore_case: bool,
    min_len: int,
    exclude: list[str],
) -> Counter[str]:
    if ignore_case:
        excluded = {w.lower() for w in exclude}
    else:
        excluded = set(exclude)

    counts: Counter[str] = Counter()
    for match in WORD_RE.finditer(text):
        word = match.group(0)
        if ignore_case:
            word = word.lower()
        if len(word) < min_len or word in excluded:
            continue
        counts[word] += 1
    return counts


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        text = read_input(args.arquivo)
    except (OSError, UnicodeDecodeError) as exc:
        msg = str(exc).replace("\r", " ").replace("\n", " ")
        sys.stderr.write(f"erro: {msg}\n")
        return 1

    counts = count_words(
        text,
        ignore_case=args.ignore_case,
        min_len=args.min_len,
        exclude=args.excluir,
    )

    top_items = heapq.nsmallest(
        args.top,
        counts.items(),
        key=lambda item: (-item[1], item[0]),
    )

    if args.formato == "json":
        payload = [
            {"palavra": word, "contagem": count}
            for word, count in top_items
        ]
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    else:
        if top_items:
            sys.stdout.write(
                "".join(f"{word}\t{count}\n" for word, count in top_items)
            )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
