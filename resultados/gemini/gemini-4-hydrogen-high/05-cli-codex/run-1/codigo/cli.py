#!/usr/bin/env python3
"""CLI para contagem de palavras em arquivos UTF-8."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import sys
from typing import Sequence


def _positive_int(value: str) -> int:
    """Converte uma string em inteiro positivo (> 0) para o argparse."""
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"valor inteiro inválido: {value!r}"
        ) from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError(
            f"o valor deve ser um inteiro positivo (> 0), recebido: {parsed}"
        )
    return parsed


def _build_parser() -> argparse.ArgumentParser:
    """Constrói uma nova instância do parser de argumentos."""
    parser = argparse.ArgumentParser(
        description="Conta a frequência de palavras em um arquivo UTF-8."
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="Caminho do arquivo de texto UTF-8 a ser lido.",
    )
    parser.add_argument(
        "--minimo",
        type=_positive_int,
        default=1,
        metavar="N",
        help="Exibe apenas palavras com contagem >= N (inteiro positivo, padrão: 1).",
    )
    parser.add_argument(
        "--top",
        type=_positive_int,
        default=None,
        metavar="N",
        help="Limita a saída aos N resultados mais frequentes após ordenar.",
    )
    parser.add_argument(
        "--ignorar-caixa",
        action="store_true",
        help="Aplica str.casefold() nos tokens antes de contar.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emite o resultado como lista JSON em uma única linha.",
    )
    return parser


def _count_words(
    path: str, *, ignore_case: bool
) -> Counter[str]:
    """Lê o arquivo UTF-8 e conta tokens separados por str.split()."""
    counts: Counter[str] = Counter()
    with open(path, "r", encoding="utf-8", errors="strict") as handle:
        text = handle.read()
    tokens = text.split()
    if ignore_case:
        counts.update(token.casefold() for token in tokens)
    else:
        counts.update(tokens)
    return counts


def _format_and_write(
    items: list[tuple[str, int]], *, as_json: bool
) -> None:
    """Formata e escreve os resultados em stdout."""
    if as_json:
        payload = [
            {"palavra": word, "contagem": count}
            for word, count in items
        ]
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
        return

    if items:
        sys.stdout.write(
            "".join(f"{word}\t{count}\n" for word, count in items)
        )


def main(argv: Sequence[str] | None = None) -> int:
    """Ponto de entrada da CLI; retorna 0 em sucesso ou 2 em erro."""
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        if exc.code is None:
            return 0
        if isinstance(exc.code, int):
            return exc.code
        return 2

    try:
        counts = _count_words(args.arquivo, ignore_case=args.ignorar_caixa)
    except (OSError, UnicodeError, ValueError) as exc:
        print(
            f"erro: não foi possível ler '{args.arquivo}': {exc}",
            file=sys.stderr,
        )
        return 2

    items = [
        (word, count)
        for word, count in counts.items()
        if count >= args.minimo
    ]
    items.sort(key=lambda item: (-item[1], item[0]))
    if args.top is not None:
        items = items[: args.top]

    _format_and_write(items, as_json=args.json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
