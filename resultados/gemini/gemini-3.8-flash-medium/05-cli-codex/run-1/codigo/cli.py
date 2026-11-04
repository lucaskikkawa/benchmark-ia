#!/usr/bin/env python3
"""Contador de palavras pela linha de comando."""

import argparse
import collections
import json
import sys
from typing import Sequence


def _positive_int(value: str) -> int:
    try:
        ivalue = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"o valor '{value}' deve ser um número inteiro positivo"
        )
    if ivalue <= 0:
        raise argparse.ArgumentTypeError(
            f"o valor '{value}' deve ser maior que zero"
        )
    return ivalue


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Contador de palavras pela linha de comando."
    )
    parser.add_argument("arquivo", metavar="ARQUIVO", help="Arquivo a ser lido")
    parser.add_argument(
        "--minimo",
        type=_positive_int,
        default=1,
        help="Inteiro positivo, padrão 1; só exibe tokens de contagem >= N",
    )
    parser.add_argument(
        "--top",
        type=_positive_int,
        default=None,
        help="Inteiro positivo opcional; limita a N resultados depois de ordenar",
    )
    parser.add_argument(
        "--ignorar-caixa",
        action="store_true",
        help="Aplica str.casefold() antes de contar",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Escreve uma lista JSON de objetos {'palavra': str, 'contagem': int}",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 2)

    try:
        with open(args.arquivo, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        sys.stderr.write(f"Erro ao ler arquivo '{args.arquivo}': {exc}\n")
        return 2

    tokens = content.split()
    if args.ignorar_caixa:
        tokens = [t.casefold() for t in tokens]

    counts = collections.Counter(tokens)

    filtered = [
        (word, count) for word, count in counts.items() if count >= args.minimo
    ]
    filtered.sort(key=lambda item: (-item[1], item[0]))

    if args.top is not None:
        filtered = filtered[: args.top]

    if args.json:
        data = [{"palavra": word, "contagem": count} for word, count in filtered]
        sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")
    else:
        if filtered:
            sys.stdout.write("".join(f"{word}\t{count}\n" for word, count in filtered))

    return 0


if __name__ == "__main__":
    sys.exit(main())
