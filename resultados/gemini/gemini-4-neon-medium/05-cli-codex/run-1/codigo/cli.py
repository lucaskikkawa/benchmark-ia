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
            f"valor inválido: {value!r} (esperado inteiro positivo)"
        ) from exc
    if parsed <= 0:
        raise argparse.ArgumentTypeError(
            f"valor deve ser um inteiro positivo, recebido: {parsed}"
        )
    return parsed


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Conta a frequência de palavras em um arquivo UTF-8.",
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="Caminho para o arquivo de texto UTF-8 a ser analisado.",
    )
    parser.add_argument(
        "--minimo",
        type=_positive_int,
        default=1,
        metavar="N",
        help="Exibe apenas tokens com contagem >= N (inteiro positivo, padrão: 1).",
    )
    parser.add_argument(
        "--top",
        type=_positive_int,
        default=None,
        metavar="N",
        help="Limita a saída aos primeiros N resultados após ordenar (inteiro positivo).",
    )
    parser.add_argument(
        "--ignorar-caixa",
        action="store_true",
        help="Aplica str.casefold() aos tokens antes de contar.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        dest="as_json",
        help="Emite a saída como uma lista JSON de objetos {'palavra', 'contagem'}.",
    )
    return parser


def _count_words(path: str, ignorar_caixa: bool) -> Counter[str]:
    counts: Counter[str] = Counter()
    with open(path, mode="r", encoding="utf-8") as handle:
        if ignorar_caixa:
            for line in handle:
                counts.update(map(str.casefold, line.split()))
        else:
            for line in handle:
                counts.update(line.split())
    return counts


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    try:
        counts = _count_words(args.arquivo, args.ignorar_caixa)
    except (OSError, UnicodeDecodeError, ValueError) as exc:
        print(f"Erro ao ler arquivo '{args.arquivo}': {exc}", file=sys.stderr)
        return 2

    items = [
        (palavra, contagem)
        for palavra, contagem in counts.items()
        if contagem >= args.minimo
    ]
    items.sort(key=lambda item: (-item[1], item[0]))

    if args.top is not None:
        items = items[: args.top]

    if args.as_json:
        payload = [
            {"palavra": palavra, "contagem": contagem}
            for palavra, contagem in items
        ]
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    elif items:
        sys.stdout.write(
            "".join(f"{palavra}\t{contagem}\n" for palavra, contagem in items)
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
