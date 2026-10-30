import argparse
from collections import Counter
import json
import sys
from typing import Optional, Sequence


def _positive_int(value: str) -> int:
    value_stripped = value.strip()
    if value_stripped.startswith("+"):
        value_stripped = value_stripped[1:]
    if not value_stripped.isascii() or not value_stripped.isdigit():
        raise argparse.ArgumentTypeError(
            f"valor inválido '{value}': esperado inteiro positivo"
        )
    parsed = int(value_stripped)
    if parsed <= 0:
        raise argparse.ArgumentTypeError(
            f"valor inválido '{value}': esperado inteiro maior que zero"
        )
    return parsed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Contador de palavras pela linha de comando.",
        allow_abbrev=False,
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="Caminho do arquivo UTF-8 a ser lido.",
    )
    parser.add_argument(
        "--minimo",
        type=_positive_int,
        default=1,
        metavar="N",
        help="Exibe apenas tokens com contagem >= N (padrão: 1).",
    )
    parser.add_argument(
        "--top",
        type=_positive_int,
        default=None,
        metavar="N",
        help="Limita a saída aos primeiros N resultados após ordenação.",
    )
    parser.add_argument(
        "--ignorar-caixa",
        action="store_true",
        help="Aplica casefold() nos tokens antes da contagem.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emite o resultado como lista JSON.",
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        if isinstance(code, int):
            return code
        return 2

    try:
        with open(args.arquivo, mode="r", encoding="utf-8", errors="strict") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as exc:
        print(f"Erro ao ler arquivo '{args.arquivo}': {exc}", file=sys.stderr)
        return 2

    tokens = content.split()
    if args.ignorar_caixa:
        tokens = [token.casefold() for token in tokens]
    counts = Counter(tokens)

    minimo = args.minimo
    filtered = [
        (word, count) for word, count in counts.items() if count >= minimo
    ]
    filtered.sort(key=lambda item: (-item[1], item[0]))

    if args.top is not None:
        filtered = filtered[: args.top]

    if args.json:
        payload = [
            {"palavra": word, "contagem": count} for word, count in filtered
        ]
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    else:
        if filtered:
            sys.stdout.write(
                "".join(f"{word}\t{count}\n" for word, count in filtered)
            )

    return 0


if __name__ == "__main__":
    sys.exit(main())
