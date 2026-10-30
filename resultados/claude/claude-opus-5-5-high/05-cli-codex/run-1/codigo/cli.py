"""Contador de palavras pela linha de comando."""

import argparse
import json
import sys
from collections import Counter


def _inteiro_positivo(texto):
    try:
        valor = int(texto)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(f"inteiro inválido: {texto!r}")
    if valor <= 0:
        raise argparse.ArgumentTypeError(f"deve ser inteiro positivo: {texto!r}")
    return valor


def _criar_parser():
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="Conta palavras (tokens de str.split()) em um arquivo UTF-8.",
    )
    parser.add_argument("arquivo", metavar="ARQUIVO", help="arquivo de texto UTF-8")
    parser.add_argument(
        "--minimo",
        type=_inteiro_positivo,
        default=1,
        metavar="N",
        help="só exibe palavras com contagem >= N (padrão: 1)",
    )
    parser.add_argument(
        "--top",
        type=_inteiro_positivo,
        default=None,
        metavar="N",
        help="limita a saída aos N primeiros resultados",
    )
    parser.add_argument(
        "--ignorar-caixa",
        action="store_true",
        help="aplica str.casefold() antes de contar",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="escreve o resultado como lista JSON",
    )
    return parser


def _contar(texto, ignorar_caixa, minimo, top):
    tokens = texto.split()
    if ignorar_caixa:
        tokens = [t.casefold() for t in tokens]
    contagens = Counter(tokens)
    resultado = [(p, c) for p, c in contagens.items() if c >= minimo]
    resultado.sort(key=lambda item: (-item[1], item[0]))
    if top is not None:
        resultado = resultado[:top]
    return resultado


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
        with open(args.arquivo, "r", encoding="utf-8") as f:
            texto = f.read()
    except UnicodeDecodeError as exc:
        sys.stderr.write(f"{parser.prog}: erro: UTF-8 inválido em {args.arquivo!r}: {exc}\n")
        return 2
    except (OSError, ValueError) as exc:
        sys.stderr.write(f"{parser.prog}: erro: não foi possível ler {args.arquivo!r}: {exc}\n")
        return 2

    resultado = _contar(texto, args.ignorar_caixa, args.minimo, args.top)

    if args.json:
        dados = [{"palavra": p, "contagem": c} for p, c in resultado]
        saida = json.dumps(dados, ensure_ascii=False) + "\n"
    else:
        saida = "".join(f"{p}\t{c}\n" for p, c in resultado)

    if saida:
        sys.stdout.write(saida)
        sys.stdout.flush()
    return 0


if __name__ == "__main__":
    for _stream in (sys.stdout, sys.stderr):
        try:
            _stream.reconfigure(encoding="utf-8")
        except (AttributeError, ValueError):
            pass
    sys.exit(main())
