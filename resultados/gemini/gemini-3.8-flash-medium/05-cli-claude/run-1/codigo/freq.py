#!/usr/bin/env python3
import argparse
from collections import Counter
import json
import os
import re
import sys


def positive_int(value: str) -> int:
    try:
        val = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(f"{value!r} não é um número inteiro válido")
    if val < 1:
        raise argparse.ArgumentTypeError(f"deve ser >= 1, mas recebeu {val}")
    return val


def read_input(file_path: str) -> str:
    try:
        if file_path == "-":
            data = sys.stdin.buffer.read()
        else:
            if os.path.isdir(file_path):
                raise IsADirectoryError(f"'{file_path}' é um diretório")
            with open(file_path, "rb") as f:
                data = f.read()
        return data.decode("utf-8")
    except Exception as e:
        msg = str(e).replace("\n", " ").strip()
        sys.stderr.write(f"erro: {msg}\n")
        sys.exit(1)


def main() -> None:
    # Ensure stdout and stderr use utf-8 encoding regardless of terminal locale
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Conta as palavras de um arquivo de texto e imprime as mais frequentes."
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="caminho do arquivo de texto (UTF-8) ou '-' para stdin",
    )
    parser.add_argument(
        "-n",
        "--top",
        metavar="N",
        type=positive_int,
        default=10,
        help="quantas palavras mostrar; inteiro >= 1; padrão 10",
    )
    parser.add_argument(
        "-m",
        "--min-len",
        metavar="K",
        type=positive_int,
        default=1,
        help="ignora palavras com menos de K caracteres; inteiro >= 1; padrão 1",
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="converte as palavras para minúsculas antes de contar",
    )
    parser.add_argument(
        "-x",
        "--excluir",
        metavar="PALAVRA",
        action="append",
        help="ignora essa palavra; pode ser repetida",
    )
    parser.add_argument(
        "--formato",
        choices=["texto", "json"],
        default="texto",
        help="formato de saída; padrão texto",
    )

    args = parser.parse_args()

    text = read_input(args.arquivo)

    # 1. Extrair as palavras do texto original
    words = re.findall(r"[^\W\d_]+", text)

    # 2. Com -i, aplicar str.lower() a cada palavra extraída
    if args.ignore_case:
        words = [w.lower() for w in words]

    # 3. Descartar as com menos de K caracteres e as excluídas por -x
    if args.excluir:
        if args.ignore_case:
            excluded = {w.lower() for w in args.excluir}
        else:
            excluded = set(args.excluir)
    else:
        excluded = set()

    filtered_words = [w for w in words if len(w) >= args.min_len and w not in excluded]

    # 4. Contar
    counts = Counter(filtered_words)

    # Ordenação: contagem decrescente; empate -> palavra em ordem crescente
    sorted_items = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    top_items = sorted_items[: args.top]

    if args.formato == "texto":
        if top_items:
            for word, count in top_items:
                print(f"{word}\t{count}")
    elif args.formato == "json":
        data = [{"palavra": word, "contagem": count} for word, count in top_items]
        print(json.dumps(data, ensure_ascii=False))


if __name__ == "__main__":
    main()
