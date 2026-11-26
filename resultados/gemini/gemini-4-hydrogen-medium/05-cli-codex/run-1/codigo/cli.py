from __future__ import annotations

import argparse
from collections import Counter
import json
import sys
from typing import Sequence


def _positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"valor inteiro positivo esperado, recebido: {value!r}"
        ) from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError(
            f"valor deve ser maior que zero, recebido: {parsed}"
        )
    return parsed


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Conta ocorrências de palavras em um arquivo UTF-8."
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="Caminho do arquivo UTF-8 a ser analisado.",
    )
    parser.add_argument(
        "--minimo",
        type=_positive_int,
        default=1,
        metavar="N",
        help="Contagem mínima para exibir uma palavra (padrão: 1).",
    )
    parser.add_argument(
        "--top",
        type=_positive_int,
        default=None,
        metavar="N",
        help="Exibe apenas os N primeiros resultados após ordenar.",
    )
    parser.add_argument(
        "--ignorar-caixa",
        action="store_true",
        help="Aplica str.casefold() às palavras antes de contar.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Escreve a saída como lista JSON em uma única linha.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    counts: Counter[str] = Counter()
    ignore_case: bool = args.ignorar_caixa
    try:
        with open(args.arquivo, "r", encoding="utf-8") as fh:
            for line in fh:
                tokens = line.split()
                if ignore_case:
                    counts.update(token.casefold() for token in tokens)
                else:
                    counts.update(tokens)
    except (OSError, UnicodeDecodeError) as exc:
        print(
            f"erro: não foi possível ler {args.arquivo!r}: {exc}",
            file=sys.stderr,
        )
        return 2

    minimo: int = args.minimo
    items = [(word, count) for word, count in counts.items() if count >= minimo]
    items.sort(key=lambda item: (-item[1], item[0]))
    if args.top is not None:
        items = items[: args.top]

    if args.json:
        payload = [{"palavra": word, "contagem": count} for word, count in items]
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    elif items:
        sys.stdout.write("".join(f"{word}\t{count}\n" for word, count in items))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
