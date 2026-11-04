#!/usr/bin/env python3
"""
CLI de frequência de palavras.
"""

import argparse
import json
import os
import re
import sys
from collections import Counter

# Garantir UTF-8 para stdout e stderr independentemente do locale
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def positive_int(value: str) -> int:
    try:
        val = int(value)
    except (ValueError, TypeError):
        raise argparse.ArgumentTypeError(f"'{value}' não é um inteiro")
    if val < 1:
        raise argparse.ArgumentTypeError(f"'{value}' deve ser um inteiro >= 1")
    return val


def parse_arguments(args=None):
    parser = argparse.ArgumentParser(
        prog="freq.py",
        description="Conta as palavras de um arquivo de texto e imprime as mais frequentes.",
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="caminho do arquivo de texto (UTF-8). - significa ler da entrada padrão.",
    )
    parser.add_argument(
        "-n",
        "--top",
        type=positive_int,
        default=10,
        metavar="N",
        help="quantas palavras mostrar; inteiro >= 1; padrão 10.",
    )
    parser.add_argument(
        "-m",
        "--min-len",
        type=positive_int,
        default=1,
        metavar="K",
        help="ignora palavras com menos de K caracteres; inteiro >= 1; padrão 1.",
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="converte as palavras para minúsculas antes de contar.",
    )
    parser.add_argument(
        "-x",
        "--excluir",
        action="append",
        default=[],
        metavar="PALAVRA",
        help="ignora essa palavra; pode ser repetida.",
    )
    parser.add_argument(
        "--formato",
        choices=["texto", "json"],
        default="texto",
        help="formato de saída; padrão texto.",
    )
    return parser.parse_args(args)


def main():
    args = parse_arguments()

    # Leitura da entrada
    try:
        if args.arquivo == "-":
            raw_data = sys.stdin.buffer.read()
        else:
            if os.path.isdir(args.arquivo):
                raise IsADirectoryError(f"Is a directory: '{args.arquivo}'")
            with open(args.arquivo, "rb") as f:
                raw_data = f.read()
        text = raw_data.decode("utf-8")
    except (OSError, UnicodeDecodeError, ValueError) as e:
        err_msg = str(e).replace("\r", " ").replace("\n", " ")
        sys.stderr.write(f"erro: {err_msg}\n")
        sys.exit(1)

    # Regra: Palavra = sequência máxima de letras Unicode (dígitos, _ e pontuação separam palavras),
    # regex [^\W\d_]+ aplicada ao texto original (sem normalização Unicode).
    # Ordem de processamento:
    # (1) extrair as palavras do texto original;
    raw_words = re.findall(r"[^\W\d_]+", text)

    # (2) com -i, aplicar str.lower() a cada palavra extraída
    if args.ignore_case:
        words = [w.lower() for w in raw_words]
        excluded = {w.lower() for w in args.excluir}
    else:
        words = raw_words
        excluded = set(args.excluir)

    # (3) descartar as com menos de K caracteres e as excluídas por -x;
    filtered_words = [w for w in words if len(w) >= args.min_len and w not in excluded]

    # (4) contar.
    counts = Counter(filtered_words)

    # Ordenação: contagem decrescente; empate -> palavra em ordem crescente (comparação simples de str).
    sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    top_items = sorted_items[: args.top]

    # Saída
    if args.formato == "texto":
        for word, count in top_items:
            print(f"{word}\t{count}")
    elif args.formato == "json":
        data = [{"palavra": word, "contagem": count} for word, count in top_items]
        print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
