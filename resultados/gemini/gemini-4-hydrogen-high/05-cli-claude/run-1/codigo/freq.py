#!/usr/bin/env python3
"""CLI de frequência de palavras em arquivos UTF-8 ou entrada padrão."""

import argparse
from collections import Counter
import json
import re
import sys

WORD_RE = re.compile(r"[^\W\d_]+")


def positive_int(value: str) -> int:
    """Converte string para inteiro >= 1 para validação no argparse."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(f"inteiro inválido: {value!r}") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError(f"deve ser >= 1, recebido {parsed}")
    return parsed


def build_parser() -> argparse.ArgumentParser:
    """Constrói e retorna o parser de argumentos da CLI."""
    parser = argparse.ArgumentParser(
        description="Conta as palavras mais frequentes de um arquivo de texto UTF-8."
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
        help="ignora a palavra informada (pode ser repetida)",
    )
    parser.add_argument(
        "--formato",
        choices=("texto", "json"),
        default="texto",
        help="formato de saída (padrão: texto)",
    )
    return parser


def read_utf8_input(path: str) -> str:
    """Lê bytes do arquivo ou de stdin e decodifica como UTF-8 estrito."""
    if path == "-":
        if hasattr(sys.stdin, "buffer"):
            raw = sys.stdin.buffer.read()
            return raw.decode("utf-8", errors="strict")
        return sys.stdin.read()

    with open(path, "rb") as handle:
        raw = handle.read()
    return raw.decode("utf-8", errors="strict")


def count_words(
    text: str,
    *,
    min_len: int,
    ignore_case: bool,
    excluded_words: list[str],
) -> Counter[str]:
    """Extrai, normaliza, filtra e conta as palavras conforme as regras da CLI."""
    excluded = (
        {word.lower() for word in excluded_words}
        if ignore_case
        else set(excluded_words)
    )
    counts: Counter[str] = Counter()
    for word in WORD_RE.findall(text):
        if ignore_case:
            word = word.lower()
        if len(word) < min_len or word in excluded:
            continue
        counts[word] += 1
    return counts


def format_output(items: list[tuple[str, int]], fmt: str) -> str:
    """Formata a lista ordenada de (palavra, contagem) para stdout."""
    if fmt == "json":
        payload = [{"palavra": word, "contagem": count} for word, count in items]
        return json.dumps(payload, ensure_ascii=False)
    return "\n".join(f"{word}\t{count}" for word, count in items)


def configure_streams() -> None:
    """Garante codificação UTF-8 independente do locale do terminal."""
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")


def main(argv: list[str] | None = None) -> int:
    configure_streams()
    parser = build_parser()
    args = parser.parse_args(argv)

    try:
        text = read_utf8_input(args.arquivo)
    except (OSError, UnicodeDecodeError) as exc:
        detail = " ".join(str(exc).splitlines()) or type(exc).__name__
        print(f"erro: {detail}", file=sys.stderr)
        return 1

    counts = count_words(
        text,
        min_len=args.min_len,
        ignore_case=args.ignore_case,
        excluded_words=args.excluir,
    )
    top_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))[: args.top]

    if args.formato == "json":
        print(format_output(top_items, "json"))
    elif top_items:
        print(format_output(top_items, "texto"))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
