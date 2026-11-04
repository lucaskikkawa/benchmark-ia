#!/usr/bin/env python3
import argparse
from collections import Counter
import json
import re
import sys

WORD_RE = re.compile(r"[^\W\d_]+")


def positive_int(value: str) -> int:
    try:
        ival = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"inteiro inválido: {value!r}") from exc
    if ival < 1:
        raise argparse.ArgumentTypeError(f"o valor deve ser >= 1: {value!r}")
    return ival


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="freq.py",
        description="Conta as palavras de um arquivo de texto e imprime as mais frequentes.",
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="Caminho do arquivo de texto (UTF-8). '-' lê da entrada padrão.",
    )
    parser.add_argument(
        "-n",
        "--top",
        type=positive_int,
        default=10,
        metavar="N",
        help="Quantas palavras mostrar (inteiro >= 1; padrão: 10).",
    )
    parser.add_argument(
        "-m",
        "--min-len",
        type=positive_int,
        default=1,
        metavar="K",
        help="Ignora palavras com menos de K caracteres (inteiro >= 1; padrão: 1).",
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="Converte as palavras para minúsculas antes de contar.",
    )
    parser.add_argument(
        "-x",
        "--excluir",
        action="append",
        default=[],
        metavar="PALAVRA",
        help="Ignora essa palavra (pode ser repetida).",
    )
    parser.add_argument(
        "--formato",
        choices=("texto", "json"),
        default="texto",
        help="Formato de saída (padrão: texto).",
    )
    return parser


def read_input(path: str) -> str:
    if path == "-":
        raw = sys.stdin.buffer.read()
        return raw.decode("utf-8", errors="strict")
    with open(path, "rb") as f:
        raw = f.read()
    return raw.decode("utf-8", errors="strict")


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
        print(f"erro: {msg}", file=sys.stderr)
        return 1

    words = WORD_RE.findall(text)
    if args.ignore_case:
        words = [w.lower() for w in words]
        excluded = {w.lower() for w in args.excluir}
    else:
        excluded = set(args.excluir)

    min_len = args.min_len
    filtered = [w for w in words if len(w) >= min_len and w not in excluded]

    counts = Counter(filtered)
    sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    top_items = sorted_items[: args.top]

    if args.formato == "json":
        result = [{"palavra": word, "contagem": count} for word, count in top_items]
        print(json.dumps(result, ensure_ascii=False))
    else:
        for word, count in top_items:
            print(f"{word}\t{count}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
