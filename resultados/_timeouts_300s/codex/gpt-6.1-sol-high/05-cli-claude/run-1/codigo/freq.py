#!/usr/bin/env python3
"""Conta palavras de um arquivo UTF-8 ou da entrada padrão."""

import argparse
from collections import Counter
import json
import re
import sys


def inteiro_positivo(valor):
    """Tipo de argumento para inteiros maiores ou iguais a um."""
    try:
        numero = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError("deve ser um inteiro >= 1") from None
    if numero < 1:
        raise argparse.ArgumentTypeError("deve ser um inteiro >= 1")
    return numero


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", metavar="ARQUIVO", help="arquivo UTF-8; - para stdin")
    parser.add_argument("-n", "--top", type=inteiro_positivo, default=10, metavar="N")
    parser.add_argument("-m", "--min-len", type=inteiro_positivo, default=1, metavar="K")
    parser.add_argument("-i", "--ignore-case", action="store_true")
    parser.add_argument("-x", "--excluir", action="append", default=[], metavar="PALAVRA")
    parser.add_argument("--formato", choices=("texto", "json"), default="texto")
    args = parser.parse_args(argv)

    try:
        # Ler bytes também em stdin evita a decodificação dependente do locale.
        if args.arquivo == "-":
            dados = sys.stdin.buffer.read()
        else:
            with open(args.arquivo, "rb") as entrada:
                dados = entrada.read()
        texto = dados.decode("utf-8", errors="strict")
    except (OSError, UnicodeError, ValueError) as erro:
        mensagem = " ".join(str(erro).splitlines())
        print("erro: " + mensagem, file=sys.stderr)
        return 1

    excluidas = set(args.excluir)
    if args.ignore_case:
        excluidas = {palavra.lower() for palavra in excluidas}

    contagens = Counter()
    for resultado in re.finditer(r"[^\W\d_]+", texto):
        palavra = resultado.group()
        if args.ignore_case:
            palavra = palavra.lower()
        if len(palavra) >= args.min_len and palavra not in excluidas:
            contagens[palavra] += 1

    frequentes = sorted(contagens.items(), key=lambda item: (-item[1], item[0]))[:args.top]
    if args.formato == "json":
        saida = json.dumps(
            [{"palavra": palavra, "contagem": total} for palavra, total in frequentes],
            ensure_ascii=False,
        ) + "\n"
    else:
        saida = "".join(f"{palavra}\t{total}\n" for palavra, total in frequentes)

    sys.stdout.buffer.write(saida.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
