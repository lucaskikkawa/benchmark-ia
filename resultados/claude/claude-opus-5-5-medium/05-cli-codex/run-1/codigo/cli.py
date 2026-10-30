"""Contador de palavras pela linha de comando."""

import argparse
import json
import sys
from collections import Counter


def _inteiro_positivo(valor):
    try:
        n = int(valor)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(f"valor inteiro inválido: {valor!r}")
    if n <= 0:
        raise argparse.ArgumentTypeError(f"deve ser um inteiro positivo: {valor!r}")
    return n


def _criar_parser():
    parser = argparse.ArgumentParser(
        prog="cli.py", description="Conta palavras de um arquivo UTF-8."
    )
    parser.add_argument("arquivo", metavar="ARQUIVO", help="arquivo de texto UTF-8")
    parser.add_argument(
        "--minimo", type=_inteiro_positivo, default=1, metavar="N",
        help="só exibe palavras com contagem >= N (padrão: 1)",
    )
    parser.add_argument(
        "--top", type=_inteiro_positivo, default=None, metavar="N",
        help="limita a saída aos N primeiros resultados",
    )
    parser.add_argument(
        "--ignorar-caixa", action="store_true",
        help="aplica casefold antes de contar",
    )
    parser.add_argument("--json", action="store_true", help="saída em JSON")
    return parser


def main(argv=None):
    parser = _criar_parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        code = exc.code
        if code is None:
            return 0
        return code if isinstance(code, int) else 2

    try:
        with open(args.arquivo, encoding="utf-8") as f:
            texto = f.read()
    except UnicodeDecodeError as exc:
        sys.stderr.write(f"cli.py: erro: {args.arquivo}: UTF-8 inválido ({exc.reason})\n")
        return 2
    except OSError as exc:
        sys.stderr.write(
            f"cli.py: erro: não foi possível ler {args.arquivo}: {exc.strerror or exc}\n"
        )
        return 2

    if args.ignorar_caixa:
        texto = texto.casefold()

    contagens = Counter(texto.split())
    resultados = sorted(
        ((p, c) for p, c in contagens.items() if c >= args.minimo),
        key=lambda item: (-item[1], item[0]),
    )
    if args.top is not None:
        resultados = resultados[: args.top]

    if args.json:
        dados = [{"palavra": p, "contagem": c} for p, c in resultados]
        saida = json.dumps(dados, ensure_ascii=False) + "\n"
    else:
        saida = "".join(f"{p}\t{c}\n" for p, c in resultados)

    if saida:
        sys.stdout.write(saida)
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    sys.exit(main())
