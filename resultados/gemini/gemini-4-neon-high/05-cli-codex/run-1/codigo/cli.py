#!/usr/bin/env python3
"""Contador de palavras pela linha de comando."""

from __future__ import annotations

import argparse
from collections import Counter
from collections.abc import Sequence
import json
import sys


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"esperado inteiro positivo, recebido: {value!r}"
        ) from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError(
            f"esperado inteiro positivo (> 0), recebido: {value!r}"
        )
    return parsed


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Conta a frequência de palavras em um arquivo UTF-8.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "arquivo",
        help="Caminho do arquivo de texto UTF-8 a ser analisado.",
    )
    parser.add_argument(
        "--minimo",
        type=_positive_int,
        default=1,
        metavar="N",
        help="Contagem mínima para exibir uma palavra (inteiro positivo, padrão: 1).",
    )
    parser.add_argument(
        "--top",
        type=_positive_int,
        default=None,
        metavar="N",
        help="Limita a saída aos N primeiros resultados após ordenação (inteiro positivo).",
    )
    parser.add_argument(
        "--ignorar-caixa",
        action="store_true",
        help="Aplica str.casefold() antes de contar as palavras.",
    )
    parser.add_argument(
        "--json",
        dest="formato_json",
        action="store_true",
        help="Emite a saída como uma lista JSON em uma única linha.",
    )
    return parser


def _count_file(path: str, *, ignore_case: bool) -> Counter[str]:
    counts: Counter[str] = Counter()
    with open(path, "r", encoding="utf-8") as handle:
        if ignore_case:
            for line in handle:
                counts.update(line.casefold().split())
        else:
            for line in handle:
                counts.update(line.split())
    return counts


def main(argv: Sequence[str] | None = None) -> int:
    """Executa a CLI e retorna o código de saída."""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        return code if isinstance(code, int) else 2

    try:
        counts = _count_file(args.arquivo, ignore_case=args.ignorar_caixa)
    except (OSError, UnicodeError, ValueError) as exc:
        sys.stderr.write(f"Erro ao ler arquivo '{args.arquivo}': {exc}\n")
        return 2

    results = [
        (word, count)
        for word, count in counts.items()
        if count >= args.minimo
    ]
    results.sort(key=lambda item: (-item[1], item[0]))
    if args.top is not None:
        results = results[: args.top]

    if args.formato_json:
        payload = [
            {"palavra": word, "contagem": count}
            for word, count in results
        ]
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    elif results:
        sys.stdout.write(
            "".join(f"{word}\t{count}\n" for word, count in results)
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
