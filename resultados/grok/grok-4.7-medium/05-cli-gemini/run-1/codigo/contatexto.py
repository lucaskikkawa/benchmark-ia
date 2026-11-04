#!/usr/bin/env python3
"""Ferramenta de contagem e métricas de texto."""

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
        raise argparse.ArgumentTypeError(
            f"valor inválido para --top: {valor!r}"
        ) from None
    if numero < 1:
        raise argparse.ArgumentTypeError("--top requer um inteiro >= 1")
    return numero


def construir_parser():
    parser = argparse.ArgumentParser(
        description="Contagem e métricas de um arquivo de texto UTF-8."
    )
    parser.add_argument(
        "arquivo",
        help="Caminho para o arquivo de texto UTF-8 a ser analisado.",
    )
    parser.add_argument(
        "-l",
        "--linhas",
        action="store_true",
        help="Contabiliza a quantidade de linhas.",
    )
    parser.add_argument(
        "-p",
        "--palavras",
        action="store_true",
        help="Contabiliza o total de palavras.",
    )
    parser.add_argument(
        "-c",
        "--chars",
        action="store_true",
        help="Contabiliza o total de caracteres.",
    )
    parser.add_argument(
        "--top",
        type=inteiro_positivo,
        metavar="N",
        help="Lista as N palavras mais frequentes (N >= 1).",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Formata o resultado como JSON.",
    )
    parser.add_argument(
        "-o",
        "--saida",
        metavar="CAMINHO",
        help="Grava a saída no caminho especificado.",
    )
    return parser


def erro(mensagem):
    texto = mensagem if mensagem.startswith("Erro") else f"Erro: {mensagem}"
    print(texto, file=sys.stderr)
    raise SystemExit(1)


def ler_conteudo(caminho):
    path = Path(caminho)
    try:
        if path.is_dir():
            erro(f"Erro: caminho é um diretório: {caminho}")
        if not path.is_file():
            erro(f"Erro: arquivo não encontrado: {caminho}")
        return path.read_text(encoding="utf-8")
    except SystemExit:
        raise
    except UnicodeDecodeError as exc:
        erro(f"Erro ao ler arquivo: {exc}")
    except OSError as exc:
        erro(f"Erro ao ler arquivo: {exc}")


def calcular_top(conteudo, n):
    contagem = Counter()
    for token in conteudo.split():
        palavra = token.lower().strip(PONTUACAO)
        if palavra:
            contagem[palavra] += 1
    ordenadas = sorted(contagem.items(), key=lambda item: (-item[1], item[0]))
    return [
        {"palavra": palavra, "ocorrencias": ocorrencias}
        for palavra, ocorrencias in ordenadas[:n]
    ]


def selecionar_metricas(conteudo, args):
    escolheu = bool(args.linhas or args.palavras or args.chars or args.top is not None)
    metricas = {}
    if (not escolheu) or args.linhas:
        metricas["linhas"] = len(conteudo.splitlines())
    if (not escolheu) or args.palavras:
        metricas["palavras"] = len(conteudo.split())
    if (not escolheu) or args.chars:
        metricas["caracteres"] = len(conteudo)
    if args.top is not None:
        metricas["top_palavras"] = calcular_top(conteudo, args.top)
    return metricas


def formatar_texto(metricas):
    linhas = []
    if "linhas" in metricas:
        linhas.append(f"Linhas: {metricas['linhas']}")
    if "palavras" in metricas:
        linhas.append(f"Palavras: {metricas['palavras']}")
    if "caracteres" in metricas:
        linhas.append(f"Caracteres: {metricas['caracteres']}")
    if "top_palavras" in metricas:
        linhas.append("Top Palavras:")
        for item in metricas["top_palavras"]:
            linhas.append(f"  - {item['palavra']}: {item['ocorrencias']}")
    return "\n".join(linhas) + "\n"


def formatar(metricas, como_json):
    if como_json:
        return json.dumps(metricas, indent=2, ensure_ascii=False) + "\n"
    return formatar_texto(metricas)


def emitir(resultado, saida):
    if saida is None:
        sys.stdout.write(resultado)
        return
    destino = Path(saida)
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(resultado, encoding="utf-8")
    except OSError as exc:
        erro(f"Erro ao gravar arquivo: {exc}")
    print(f"Salvo em {saida}")


def main(argv=None):
    parser = construir_parser()
    args = parser.parse_args(argv)
    conteudo = ler_conteudo(args.arquivo)
    metricas = selecionar_metricas(conteudo, args)
    emitir(formatar(metricas, args.json), args.saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
