#!/usr/bin/env python3
"""Contagem e métricas de texto em linha de comando."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

PONTUACAO = ".,!?;:\"'()[]{}"


def inteiro_positivo(valor):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(
            f"valor inválido para --top: {valor!r}"
        ) from None
    if numero < 1:
        raise argparse.ArgumentTypeError("--top deve ser um inteiro >= 1")
    return numero


def construir_parser():
    parser = argparse.ArgumentParser(
        description="Contagem e métricas de um arquivo de texto UTF-8."
    )
    parser.add_argument("arquivo", metavar="ARQUIVO")
    parser.add_argument("-l", "--linhas", action="store_true")
    parser.add_argument("-p", "--palavras", action="store_true")
    parser.add_argument("-c", "--chars", action="store_true")
    parser.add_argument("--top", type=inteiro_positivo, metavar="N")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("-o", "--saida", metavar="CAMINHO")
    return parser


def ler_arquivo(caminho):
    path = Path(caminho)
    if not path.exists():
        print(f"Erro: arquivo não encontrado: {caminho}", file=sys.stderr)
        return None
    if path.is_dir():
        print(f"Erro: caminho é um diretório: {caminho}", file=sys.stderr)
        return None
    if not path.is_file():
        print(f"Erro: caminho não é um arquivo regular: {caminho}", file=sys.stderr)
        return None
    try:
        # newline="" preserva \r e \r\n para len(conteudo) e splitlines().
        with path.open(encoding="utf-8", newline="") as arquivo:
            return arquivo.read()
    except UnicodeDecodeError as exc:
        print(f"Erro ao ler arquivo: {exc}", file=sys.stderr)
        return None
    except OSError as exc:
        print(f"Erro ao ler arquivo: {exc}", file=sys.stderr)
        return None


def palavras_frequentes(conteudo, limite):
    contagem = Counter()
    for token in conteudo.split():
        palavra = token.lower().strip(PONTUACAO)
        if palavra:
            contagem[palavra] += 1
    ordenadas = sorted(contagem.items(), key=lambda item: (-item[1], item[0]))
    return ordenadas[:limite]


def metricas_selecionadas(args):
    alguma = args.linhas or args.palavras or args.chars or args.top is not None
    return {
        "linhas": args.linhas or not alguma,
        "palavras": args.palavras or not alguma,
        "caracteres": args.chars or not alguma,
        "top": args.top is not None,
    }


def calcular(conteudo, args):
    flags = metricas_selecionadas(args)
    resultado = {}
    if flags["linhas"]:
        resultado["linhas"] = len(conteudo.splitlines())
    if flags["palavras"]:
        resultado["palavras"] = len(conteudo.split())
    if flags["caracteres"]:
        resultado["caracteres"] = len(conteudo)
    if flags["top"]:
        resultado["top_palavras"] = [
            {"palavra": palavra, "ocorrencias": ocorrencias}
            for palavra, ocorrencias in palavras_frequentes(conteudo, args.top)
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


def formatar_json(resultado):
    return json.dumps(resultado, indent=2, ensure_ascii=False) + "\n"


def gravar_saida(caminho, conteudo):
    destino = Path(caminho)
    try:
        destino.parent.mkdir(parents=True, exist_ok=True)
        with destino.open("w", encoding="utf-8", newline="\n") as arquivo:
            arquivo.write(conteudo)
    except OSError as exc:
        print(f"Erro ao gravar arquivo: {exc}", file=sys.stderr)
        return False
    return True


def main(argv=None):
    parser = construir_parser()
    args = parser.parse_args(argv)

    conteudo = ler_arquivo(args.arquivo)
    if conteudo is None:
        return 1

    resultado = calcular(conteudo, args)
    saida = formatar_json(resultado) if args.json else formatar_texto(resultado)

    if args.saida is not None:
        if not gravar_saida(args.saida, saida):
            return 1
        sys.stdout.write(f"Salvo em {args.saida}\n")
    else:
        sys.stdout.write(saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
