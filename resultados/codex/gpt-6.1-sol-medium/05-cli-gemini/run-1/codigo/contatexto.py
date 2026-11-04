"""Ferramenta de linha de comando para contar e analisar texto UTF-8."""

import argparse
from collections import Counter
import json
from pathlib import Path
import sys


PONTUACAO = ".,!?;:\"'()[]{}"


def inteiro_positivo(valor):
    """Valida o limite de palavras usando os erros de sintaxe do argparse."""
    try:
        numero = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError("deve ser um inteiro >= 1") from None
    if numero < 1:
        raise argparse.ArgumentTypeError("deve ser um inteiro >= 1")
    return numero


def analisar(conteudo, args):
    resultado = {}
    padrao = not (args.linhas or args.palavras or args.chars or args.top)
    if padrao or args.linhas:
        resultado["linhas"] = len(conteudo.splitlines())
    if padrao or args.palavras:
        resultado["palavras"] = len(conteudo.split())
    if padrao or args.chars:
        resultado["caracteres"] = len(conteudo)
    if args.top is not None:
        tokens = (token.lower().strip(PONTUACAO) for token in conteudo.split())
        frequencias = Counter(token for token in tokens if token)
        ordenadas = sorted(frequencias.items(), key=lambda item: (-item[1], item[0]))
        resultado["top_palavras"] = [
            {"palavra": palavra, "ocorrencias": ocorrencias}
            for palavra, ocorrencias in ordenadas[:args.top]
        ]
    return resultado


def formatar(resultado, usar_json):
    if usar_json:
        return json.dumps(resultado, indent=2, ensure_ascii=False)
    rotulos = {"linhas": "Linhas", "palavras": "Palavras", "caracteres": "Caracteres"}
    linhas = []
    for metrica, valor in resultado.items():
        if metrica == "top_palavras":
            linhas.append("Top Palavras:")
            linhas.extend(
                f"  - {item['palavra']}: {item['ocorrencias']}" for item in valor
            )
        else:
            linhas.append(f"{rotulos[metrica]}: {valor}")
    return "\n".join(linhas)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("arquivo", metavar="ARQUIVO", help="arquivo de texto UTF-8")
    parser.add_argument("-l", "--linhas", action="store_true", help="contar linhas")
    parser.add_argument("-p", "--palavras", action="store_true", help="contar palavras")
    parser.add_argument("-c", "--chars", action="store_true", help="contar caracteres")
    parser.add_argument("--top", type=inteiro_positivo, metavar="N", help="listar as N palavras mais frequentes")
    parser.add_argument("--json", action="store_true", help="formatar como JSON")
    parser.add_argument("-o", "--saida", metavar="CAMINHO", help="salvar resultado em arquivo")
    args = parser.parse_args(argv)

    try:
        entrada = Path(args.arquivo)
        if not entrada.is_file():
            raise OSError(f"'{args.arquivo}' não é um arquivo regular existente")
        with entrada.open("r", encoding="utf-8", newline="") as arquivo:
            conteudo = arquivo.read()
        saida = formatar(analisar(conteudo, args), args.json) + "\n"
        if args.saida is not None:
            destino = Path(args.saida)
            destino.parent.mkdir(parents=True, exist_ok=True)
            with destino.open("w", encoding="utf-8", newline="") as arquivo:
                arquivo.write(saida)
            print(f"Salvo em {args.saida}")
        else:
            sys.stdout.write(saida)
    except (OSError, UnicodeError, ValueError) as erro:
        print(f"Erro: {erro}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
