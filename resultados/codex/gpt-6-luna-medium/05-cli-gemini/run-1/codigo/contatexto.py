#!/usr/bin/env python3
"""Conta métricas básicas de um arquivo de texto UTF-8."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path


PONTUACAO = '.,!?;:"\'()[]{}'


def inteiro_positivo(valor):
    try:
        numero = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError("deve ser um inteiro")
    if numero < 1:
        raise argparse.ArgumentTypeError("deve ser maior ou igual a 1")
    return numero


def formatar_texto(metricas):
    linhas = []
    rotulos = {
        "linhas": "Linhas",
        "palavras": "Palavras",
        "caracteres": "Caracteres",
    }
    for chave in ("linhas", "palavras", "caracteres"):
        if chave in metricas:
            linhas.append(f"{rotulos[chave]}: {metricas[chave]}")
    if "top_palavras" in metricas:
        linhas.append("Top Palavras:")
        linhas.extend(
            f"  - {item['palavra']}: {item['ocorrencias']}"
            for item in metricas["top_palavras"]
        )
    return "\n".join(linhas) + "\n"


def main(argv=None):
    parser = argparse.ArgumentParser(description="Conta métricas de um arquivo de texto.")
    parser.add_argument("arquivo", help="arquivo de texto UTF-8 a analisar")
    parser.add_argument("-l", "--linhas", action="store_true", help="conta linhas")
    parser.add_argument("-p", "--palavras", action="store_true", help="conta palavras")
    parser.add_argument("-c", "--chars", action="store_true", help="conta caracteres")
    parser.add_argument("--top", type=inteiro_positivo, metavar="N", help="mostra as N palavras mais frequentes")
    parser.add_argument("--json", action="store_true", help="formata a saída como JSON")
    parser.add_argument("-o", "--saida", metavar="CAMINHO", help="grava a saída em um arquivo")
    args = parser.parse_args(argv)

    caminho = Path(args.arquivo)
    try:
        if not caminho.is_file():
            raise OSError("o caminho não aponta para um arquivo regular")
        conteudo = caminho.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as erro:
        print(f"Erro ao ler arquivo: {erro}", file=sys.stderr)
        return 1

    alguma_metrica = args.linhas or args.palavras or args.chars or args.top is not None
    selecionar_todas = not alguma_metrica
    metricas = {}
    if args.linhas or selecionar_todas:
        metricas["linhas"] = len(conteudo.splitlines())
    if args.palavras or selecionar_todas:
        metricas["palavras"] = len(conteudo.split())
    if args.chars or selecionar_todas:
        metricas["caracteres"] = len(conteudo)
    if args.top is not None:
        frequencias = Counter(
            token.lower().strip(PONTUACAO)
            for token in conteudo.split()
        )
        frequencias.pop("", None)
        ranking = sorted(frequencias.items(), key=lambda item: (-item[1], item[0]))[:args.top]
        metricas["top_palavras"] = [
            {"palavra": palavra, "ocorrencias": quantidade}
            for palavra, quantidade in ranking
        ]

    if args.json:
        saida = json.dumps(metricas, indent=2, ensure_ascii=False) + "\n"
    else:
        saida = formatar_texto(metricas)

    if args.saida is not None:
        try:
            destino = Path(args.saida)
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_text(saida, encoding="utf-8")
        except OSError as erro:
            print(f"Erro ao salvar arquivo: {erro}", file=sys.stderr)
            return 1
        print(f"Salvo em {args.saida}")
    else:
        sys.stdout.write(saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
