from __future__ import annotations

import argparse
from collections import Counter
import json
import sys
from typing import Sequence


def _inteiro_positivo(valor: str) -> int:
    try:
        numero = int(valor)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(
            f"valor inválido '{valor}': esperado inteiro positivo"
        ) from exc
    if numero <= 0:
        raise argparse.ArgumentTypeError(
            f"valor inválido '{valor}': esperado inteiro maior que zero"
        )
    return numero


def _criar_parser() -> argparse.ArgumentParser:
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
        type=_inteiro_positivo,
        default=1,
        metavar="N",
        help="Inteiro positivo (padrão 1); só exibe tokens de contagem >= N.",
    )
    parser.add_argument(
        "--top",
        type=_inteiro_positivo,
        default=None,
        metavar="N",
        help="Inteiro positivo opcional; limita a N resultados após ordenar.",
    )
    parser.add_argument(
        "--ignorar-caixa",
        action="store_true",
        help="Aplica str.casefold() antes de contar.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Escreve o resultado como lista JSON de objetos.",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    parser = _criar_parser()
    try:
        args = parser.parse_args(None if argv is None else list(argv))
    except SystemExit as exc:
        return exc.code if isinstance(exc.code, int) else 2

    try:
        with open(args.arquivo, "r", encoding="utf-8") as f:
            conteudo = f.read()
    except (OSError, UnicodeError, ValueError) as exc:
        print(f"Erro ao ler arquivo '{args.arquivo}': {exc}", file=sys.stderr)
        return 2

    if args.ignorar_caixa:
        conteudo = conteudo.casefold()

    contagens = Counter(conteudo.split())

    itens = [
        (palavra, contagem)
        for palavra, contagem in contagens.items()
        if contagem >= args.minimo
    ]
    itens.sort(key=lambda item: (-item[1], item[0]))

    if args.top is not None:
        itens = itens[: args.top]

    if args.json:
        dados = [
            {"palavra": palavra, "contagem": contagem}
            for palavra, contagem in itens
        ]
        sys.stdout.write(json.dumps(dados, ensure_ascii=False) + "\n")
    elif itens:
        sys.stdout.write(
            "".join(f"{palavra}\t{contagem}\n" for palavra, contagem in itens)
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
