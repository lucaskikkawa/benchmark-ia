"""Ferramenta de linha de comando para contagem e métricas de texto."""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys


PONTUACAO = ".,!?;:\"'()[]{}"


def inteiro_positivo(valor):
    """Valida o argumento --top usando os erros de sintaxe do argparse."""
    try:
        numero = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError("deve ser um inteiro maior ou igual a 1")
    if numero < 1:
        raise argparse.ArgumentTypeError("deve ser um inteiro maior ou igual a 1")
    return numero


def criar_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", metavar="ARQUIVO", help="arquivo de texto UTF-8")
    parser.add_argument("-l", "--linhas", action="store_true", help="contar linhas")
    parser.add_argument("-p", "--palavras", action="store_true", help="contar palavras")
    parser.add_argument("-c", "--chars", action="store_true", help="contar caracteres")
    parser.add_argument("--top", type=inteiro_positivo, metavar="N",
                        help="listar as N palavras mais frequentes")
    parser.add_argument("--json", action="store_true", help="gerar saída JSON")
    parser.add_argument("-o", "--saida", metavar="CAMINHO", help="gravar saída em arquivo")
    return parser


def calcular_metricas(conteudo, args):
    padrao = not (args.linhas or args.palavras or args.chars or args.top is not None)
    metricas = {}
    if padrao or args.linhas:
        metricas["linhas"] = len(conteudo.splitlines())
    if padrao or args.palavras:
        metricas["palavras"] = len(conteudo.split())
    if padrao or args.chars:
        metricas["caracteres"] = len(conteudo)
    if args.top is not None:
        palavras = (token.lower().strip(PONTUACAO) for token in conteudo.split())
        frequencias = Counter(palavra for palavra in palavras if palavra)
        ranking = sorted(frequencias.items(), key=lambda item: (-item[1], item[0]))
        metricas["top_palavras"] = [
            {"palavra": palavra, "ocorrencias": ocorrencias}
            for palavra, ocorrencias in ranking[:args.top]
        ]
    return metricas


def formatar_texto(metricas):
    rotulos = {"linhas": "Linhas", "palavras": "Palavras", "caracteres": "Caracteres"}
    linhas = []
    for chave, valor in metricas.items():
        if chave == "top_palavras":
            linhas.append("Top Palavras:")
            linhas.extend(
                f"  - {item['palavra']}: {item['ocorrencias']}" for item in valor
            )
        else:
            linhas.append(f"{rotulos[chave]}: {valor}")
    return "\n".join(linhas)


def main(argv=None):
    args = criar_parser().parse_args(argv)
    try:
        caminho = Path(args.arquivo)
        if not caminho.is_file():
            raise OSError(f"o caminho não é um arquivo regular existente: {args.arquivo}")
        # Preserva as quebras originais, inclusive CRLF, na contagem de caracteres.
        with caminho.open("r", encoding="utf-8", newline="") as arquivo:
            conteudo = arquivo.read()

        metricas = calcular_metricas(conteudo, args)
        resultado = (json.dumps(metricas, indent=2, ensure_ascii=False)
                     if args.json else formatar_texto(metricas))
        if args.saida is not None:
            destino = Path(args.saida)
            destino.parent.mkdir(parents=True, exist_ok=True)
            with destino.open("w", encoding="utf-8", newline="") as arquivo:
                arquivo.write(resultado + "\n")
            print(f"Salvo em {args.saida}")
        else:
            print(resultado)
    except (OSError, UnicodeError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
