#!/usr/bin/env python3
"""Ferramenta CLI de contagem e métricas de texto."""

import argparse
import json
import os
import sys
from collections import Counter

PONTUACAO = ".,!?;:\"'()[]{}"


def inteiro_positivo(valor):
    try:
        n = int(valor)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(f"valor inválido: {valor!r} (esperado inteiro >= 1)")
    if n < 1:
        raise argparse.ArgumentTypeError(f"valor inválido: {n} (deve ser >= 1)")
    return n


def criar_parser():
    parser = argparse.ArgumentParser(
        prog="contatexto.py",
        description="Conta linhas, palavras, caracteres e palavras mais frequentes de um arquivo de texto.",
    )
    parser.add_argument("arquivo", metavar="ARQUIVO", help="arquivo de texto UTF-8 a ser analisado")
    parser.add_argument("-l", "--linhas", action="store_true", help="conta linhas")
    parser.add_argument("-p", "--palavras", action="store_true", help="conta palavras")
    parser.add_argument("-c", "--chars", action="store_true", help="conta caracteres")
    parser.add_argument("--top", type=inteiro_positivo, metavar="N", help="lista as N palavras mais frequentes")
    parser.add_argument("--json", action="store_true", help="saída em formato JSON")
    parser.add_argument("-o", "--saida", metavar="CAMINHO", help="grava a saída no arquivo indicado")
    return parser


def top_palavras(conteudo, n):
    tokens = (t.lower().strip(PONTUACAO) for t in conteudo.split())
    contagem = Counter(t for t in tokens if t)
    ordenado = sorted(contagem.items(), key=lambda kv: (-kv[1], kv[0]))
    return ordenado[:n]


def calcular(conteudo, args):
    nenhuma = not (args.linhas or args.palavras or args.chars or args.top is not None)
    resultado = {}
    if nenhuma or args.linhas:
        resultado["linhas"] = len(conteudo.splitlines())
    if nenhuma or args.palavras:
        resultado["palavras"] = len(conteudo.split())
    if nenhuma or args.chars:
        resultado["caracteres"] = len(conteudo)
    if args.top is not None:
        resultado["top_palavras"] = [
            {"palavra": p, "ocorrencias": c} for p, c in top_palavras(conteudo, args.top)
        ]
    return resultado


def formatar_texto(resultado):
    linhas = []
    if "linhas" in resultado:
        linhas.append(f"Linhas: {resultado['linhas']}")
    if "palavras" in resultado:
        linhas.append(f"Palavras: {resultado['palavras']}")
    if "caracteres" in resultado:
        linhas.append(f"Caracteres: {resultado['caracteres']}")
    if "top_palavras" in resultado:
        linhas.append("Top Palavras:")
        for item in resultado["top_palavras"]:
            linhas.append(f"  - {item['palavra']}: {item['ocorrencias']}")
    return "\n".join(linhas) + "\n"


def main(argv=None):
    args = criar_parser().parse_args(argv)

    if not os.path.exists(args.arquivo):
        print(f"Erro: arquivo não encontrado: {args.arquivo}", file=sys.stderr)
        return 1
    if not os.path.isfile(args.arquivo):
        print(f"Erro: o caminho não é um arquivo regular: {args.arquivo}", file=sys.stderr)
        return 1
    try:
        with open(args.arquivo, "r", encoding="utf-8", newline="") as f:
            conteudo = f.read()
    except (OSError, UnicodeDecodeError) as e:
        print(f"Erro ao ler arquivo: {e}", file=sys.stderr)
        return 1

    resultado = calcular(conteudo, args)
    if args.json:
        saida = json.dumps(resultado, indent=2, ensure_ascii=False) + "\n"
    else:
        saida = formatar_texto(resultado)

    if args.saida:
        try:
            pasta = os.path.dirname(args.saida)
            if pasta:
                os.makedirs(pasta, exist_ok=True)
            with open(args.saida, "w", encoding="utf-8", newline="") as f:
                f.write(saida)
        except OSError as e:
            print(f"Erro ao gravar arquivo: {e}", file=sys.stderr)
            return 1
        sys.stdout.write(f"Salvo em {args.saida}\n")
    else:
        sys.stdout.write(saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
