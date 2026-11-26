#!/usr/bin/env python3
"""CLI para contagem de frequência de palavras em arquivos UTF-8 ou stdin."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import re
import sys

WORD_RE = re.compile(r"[^\W\d_]+")


def positive_int(value: str) -> int:
    """Converte uma string para inteiro >= 1 para validação no argparse."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"inteiro inválido: {value!r}") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError(f"o valor deve ser >= 1 (recebido: {parsed})")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    """Constrói e retorna o parser de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        description="Conta as palavras mais frequentes de um arquivo UTF-8 ou stdin."
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="Caminho do arquivo de texto (UTF-8), ou '-' para ler da entrada padrão.",
    )
    parser.add_argument(
        "-n",
        "--top",
        type=positive_int,
        default=10,
        metavar="N",
        help="Quantas palavras mostrar (>= 1; padrão: 10).",
    )
    parser.add_argument(
        "-m",
        "--min-len",
        type=positive_int,
        default=1,
        metavar="K",
        help="Ignora palavras com menos de K caracteres (>= 1; padrão: 1).",
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Converte palavras para minúsculas (str.lower) antes de contar.",
    )
    parser.add_argument(
        "-x",
        "--excluir",
        action="append",
        default=[],
        metavar="PALAVRA",
        help="Palavra a ignorar; pode ser repetida.",
    )
    parser.add_argument(
        "--formato",
        choices=("texto", "json"),
        default="texto",
        help="Formato de saída (padrão: texto).",
    )
    return parser


def read_utf8_input(path: str) -> str:
    """Lê todo o conteúdo de um arquivo ou stdin e decodifica como UTF-8 estrito."""
    if path == "-":
        raw = sys.stdin.buffer.read()
    else:
        with open(path, "rb") as handle:
            raw = handle.read()
    return raw.decode("utf-8", errors="strict")


def count_words(
    text: str,
    *,
    ignore_case: bool,
    min_len: int,
    excluded: list[str],
    top: int,
) -> list[tuple[str, int]]:
    """Extrai, filtra, conta e ordena as palavras mais frequentes."""
    excluded_set = {w.lower() if ignore_case else w for w in excluded}
    counts: Counter[str] = Counter()

    for word in WORD_RE.findall(text):
        normalized = word.lower() if ignore_case else word
        if len(normalized) < min_len or normalized in excluded_set:
            continue
        counts[normalized] += 1

    ordered = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    return ordered[:top]


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        text = read_utf8_input(args.arquivo)
    except (OSError, UnicodeDecodeError) as exc:
        detail = str(exc).replace("\n", " ")
        print(f"erro: {detail}", file=sys.stderr)
        return 1

    results = count_words(
        text,
        ignore_case=args.ignore_case,
        min_len=args.min_len,
        excluded=args.excluir,
        top=args.top,
    )

    if args.formato == "json":
        payload = [{"palavra": word, "contagem": count} for word, count in results]
        print(json.dumps(payload, ensure_ascii=False))
    else:
        for word, count in results:
            print(f"{word}\t{count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
