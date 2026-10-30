#!/usr/bin/env python3
"""Ferramenta CLI de contagem e métricas de texto."""

import argparse
import json
import os
import sys
from collections import Counter

PONTUACAO = '.,!?;:"\'()[]{}'


def positive_int(valor):
    try:
        numero = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"valor inválido: {valor!r}")
    if numero < 1:
        raise argparse.ArgumentTypeError("deve ser um inteiro maior ou igual a 1")
    return numero


def construir_parser():
    parser = argparse.ArgumentParser(
        description="Contagem e métricas de um arquivo de texto UTF-8."
    )
    parser.add_argument("arquivo", metavar="ARQUIVO",
                        help="caminho para o arquivo de texto UTF-8")
    parser.add_argument("-l", "--linhas", action="store_true",
                        help="contabiliza as linhas")
    parser.add_argument("-p", "--palavras", action="store_true",
                        help="contabiliza as palavras")
    parser.add_argument("-c", "--chars", action="store_true",
                        help="contabiliza os caracteres")
    parser.add_argument("--top", type=positive_int, metavar="N",
                        help="lista as N palavras mais frequentes")
    parser.add_argument("--json", action="store_true",
                        help="formata o resultado como JSON")
    parser.add_argument("-o", "--saida", metavar="CAMINHO",
                        help="grava a saída no arquivo indicado")
    return parser


def erro(mensagem):
    print(mensagem, file=sys.stderr)
    sys.exit(1)


def ler_arquivo(caminho):
    if not os.path.exists(caminho):
        erro(f"Erro: arquivo não encontrado: {caminho}")
    if not os.path.isfile(caminho):
        erro(f"Erro: o caminho não é um arquivo regular: {caminho}")
    try:
        with open(caminho, "r", encoding="utf-8") as arquivo:
            return arquivo.read()
    except UnicodeDecodeError as exc:
        erro(f"Erro ao ler arquivo: falha de decodificação UTF-8 ({exc})")
    except OSError as exc:
        erro(f"Erro ao ler arquivo: {exc}")


def top_palavras(conteudo, n):
    contagem = Counter()
    for token in conteudo.split():
        palavra = token.lower().strip(PONTUACAO)
        if palavra:
            contagem[palavra] += 1
    ordenadas = sorted(contagem.items(), key=lambda item: (-item[1], item[0]))
    return ordenadas[:n]


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
    return "\n".join(linhas)


def formatar_json(resultado):
    return json.dumps(resultado, indent=2, ensure_ascii=False)


def main():
    parser = construir_parser()
    args = parser.parse_args()

    selecionadas = args.linhas or args.palavras or args.chars or args.top is not None
    if not selecionadas:
        args.linhas = args.palavras = args.chars = True

    conteudo = ler_arquivo(args.arquivo)

    resultado = {}
    if args.linhas:
        resultado["linhas"] = len(conteudo.splitlines())
    if args.palavras:
        resultado["palavras"] = len(conteudo.split())
    if args.chars:
        resultado["caracteres"] = len(conteudo)
    if args.top is not None:
        resultado["top_palavras"] = [
            {"palavra": palavra, "ocorrencias": ocorrencias}
            for palavra, ocorrencias in top_palavras(conteudo, args.top)
        ]

    saida = formatar_json(resultado) if args.json else formatar_texto(resultado)

    if args.saida:
        diretorio = os.path.dirname(args.saida)
        try:
            if diretorio:
                os.makedirs(diretorio, exist_ok=True)
            with open(args.saida, "w", encoding="utf-8") as arquivo:
                arquivo.write(saida + "\n")
        except OSError as exc:
            erro(f"Erro ao gravar arquivo de saída: {exc}")
        print(f"Salvo em {args.saida}")
    else:
        print(saida)


if __name__ == "__main__":
    main()
