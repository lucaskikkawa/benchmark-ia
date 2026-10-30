"""Contador de palavras pela linha de comando."""

import argparse
import collections
import json
import sys


def positive_int(value: str) -> int:
    """Valida se o valor informado é um inteiro positivo (> 0)."""
    try:
        val = int(value)
    except (ValueError, TypeError):
        raise argparse.ArgumentTypeError(
            f"Valor inválido: {value!r} (deve ser um número inteiro)."
        )
    if val <= 0:
        raise argparse.ArgumentTypeError(
            f"Valor inválido: {value!r} (deve ser maior que zero)."
        )
    return val


def create_parser() -> argparse.ArgumentParser:
    """Cria e configura o analisador de argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Contador de palavras pela linha de comando",
    )
    parser.add_argument(
        "ARQUIVO",
        help="Caminho do arquivo UTF-8 a ser lido",
    )
    parser.add_argument(
        "--minimo",
        type=positive_int,
        default=1,
        help="inteiro positivo, padrão 1; só exibe tokens de contagem >= N",
    )
    parser.add_argument(
        "--top",
        type=positive_int,
        default=None,
        help="inteiro positivo opcional; limita a N resultados depois de ordenar",
    )
    parser.add_argument(
        "--ignorar-caixa",
        action="store_true",
        help="aplica str.casefold() antes de contar",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="escreve uma lista JSON de objetos {'palavra': str, 'contagem': int}",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    """Ponto de entrada da CLI."""
    if argv is None:
        argv = sys.argv[1:]

    parser = create_parser()

    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else (0 if exc.code is None else 2)

    try:
        with open(args.ARQUIVO, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeError) as exc:
        sys.stderr.write(f"Erro ao ler arquivo: {exc}\n")
        return 2
    except Exception as exc:
        sys.stderr.write(f"Erro inesperado: {exc}\n")
        return 2

    tokens = content.split()
    if args.ignorar_caixa:
        counts = collections.Counter(t.casefold() for t in tokens)
    else:
        counts = collections.Counter(tokens)

    results = [(word, count) for word, count in counts.items() if count >= args.minimo]
    results.sort(key=lambda item: (-item[1], item[0]))

    if args.top is not None:
        results = results[: args.top]

    if args.json:
        data = [{"palavra": word, "contagem": count} for word, count in results]
        sys.stdout.write(json.dumps(data, ensure_ascii=False) + "\n")
    else:
        for word, count in results:
            sys.stdout.write(f"{word}\t{count}\n")

    return 0


if __name__ == "__main__":
    sys.exit(main())
