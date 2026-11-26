#!/usr/bin/env python3
from __future__ import annotations

import argparse
from collections import Counter
import io
import json
import re
import sys
from typing import Iterable

WORD_RE = re.compile(r"[^\W\d_]+")


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"valor inteiro inválido: {value!r}") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError(f"deve ser um inteiro >= 1: {value!r}")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
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
        help="converte palavras para minúsculas antes de contar",
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


def count_words(
    lines: Iterable[str],
    *,
    ignore_case: bool,
    min_len: int,
    excluded: set[str],
) -> Counter[str]:
    counts: Counter[str] = Counter()
    for line in lines:
        for match in WORD_RE.finditer(line):
            word = match.group(0)
            if ignore_case:
                word = word.lower()
            if len(word) < min_len or word in excluded:
                continue
            counts[word] += 1
    return counts


def read_and_count(
    arquivo: str,
    *,
    ignore_case: bool,
    min_len: int,
    excluded: set[str],
) -> Counter[str]:
    if arquivo == "-":
        stream = io.TextIOWrapper(sys.stdin.buffer, encoding="utf-8", errors="strict")
        try:
            return count_words(
                stream,
                ignore_case=ignore_case,
                min_len=min_len,
                excluded=excluded,
            )
        finally:
            stream.detach()
    with open(arquivo, mode="r", encoding="utf-8", errors="strict") as f:
        return count_words(
            f,
            ignore_case=ignore_case,
            min_len=min_len,
            excluded=excluded,
        )


def main(argv: list[str] | None = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    parser = build_parser()
    args = parser.parse_args(argv)

    excluded = (
        {word.lower() for word in args.excluir}
        if args.ignore_case
        else set(args.excluir)
    )

    try:
        counts = read_and_count(
            args.arquivo,
            ignore_case=args.ignore_case,
            min_len=args.min_len,
            excluded=excluded,
        )
    except (OSError, UnicodeDecodeError) as exc:
        msg = str(exc).replace("\r", " ").replace("\n", " ")
        sys.stderr.write(f"erro: {msg}\n")
        return 1

    top_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[: args.top]

    if args.formato == "json":
        payload = [{"palavra": word, "contagem": count} for word, count in top_items]
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    else:
        for word, count in top_items:
            sys.stdout.write(f"{word}\t{count}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
