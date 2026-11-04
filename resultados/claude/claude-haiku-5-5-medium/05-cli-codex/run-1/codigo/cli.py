"""Contador de palavras pela linha de comando.

Uso: python cli.py ARQUIVO [--minimo N] [--top N] [--ignorar-caixa] [--json]
"""

import argparse
import json
import re
import sys
from collections import Counter


def _inteiro_positivo(texto):
    if not re.fullmatch(r"\+?[0-9]+", texto):
        raise argparse.ArgumentTypeError(f"esperado inteiro positivo, recebido {texto!r}")
    valor = int(texto)
    if valor < 1:
        raise argparse.ArgumentTypeError(f"esperado inteiro positivo, recebido {texto!r}")
    return valor


class _Parser(argparse.ArgumentParser):
    def error(self, message):
        self.print_usage(sys.stderr)
        self.exit(2, f"{self.prog}: erro: {message}\n")


def _construir_parser():
    parser = _Parser(
        prog="cli.py",
        description="Conta palavras (tokens de str.split()) de um arquivo UTF-8.",
    )
    parser.add_argument("arquivo", metavar="ARQUIVO", help="arquivo UTF-8 a ser lido")
    parser.add_argument(
        "--minimo", type=_inteiro_positivo, default=1, metavar="N",
        help="exibe apenas tokens com contagem >= N (padrão: 1)",
    )
    parser.add_argument(
        "--top", type=_inteiro_positivo, default=None, metavar="N",
        help="limita a N resultados após ordenar",
    )
    parser.add_argument(
        "--ignorar-caixa", action="store_true",
        help="aplica str.casefold() antes de contar",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="escreve a saída como lista JSON de objetos",
    )
    return parser


def main(argv=None) -> int:
    try:
        args = _construir_parser().parse_args(argv)
    except SystemExit as saida:
        return saida.code if isinstance(saida.code, int) else 2

    try:
        with open(args.arquivo, encoding="utf-8") as arq:
            texto = arq.read()
    except UnicodeDecodeError:
        sys.stderr.write(f"erro: {args.arquivo!r} não é UTF-8 válido\n")
        return 2
    except OSError as exc:
        sys.stderr.write(f"erro: não foi possível ler {args.arquivo!r}: {exc.strerror}\n")
        return 2

    contagens = Counter()
    for token in texto.split():
        if args.ignorar_caixa:
            token = token.casefold()
        contagens[token] += 1

    resultados = [(p, c) for p, c in contagens.items() if c >= args.minimo]
    resultados.sort(key=lambda item: (-item[1], item[0]))
    if args.top is not None:
        resultados = resultados[: args.top]

    if args.json:
        dados = [{"palavra": p, "contagem": c} for p, c in resultados]
        sys.stdout.write(json.dumps(dados, ensure_ascii=False) + "\n")
    else:
        for palavra, contagem in resultados:
            sys.stdout.write(f"{palavra}\t{contagem}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
