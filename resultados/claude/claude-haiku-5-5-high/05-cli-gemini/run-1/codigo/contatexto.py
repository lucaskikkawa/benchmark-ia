import argparse
import json
import os
import sys
from collections import Counter

PONTUACAO = '.,!?;:"\'()[]{}'


def inteiro_positivo(valor):
    try:
        numero = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"valor inválido: {valor!r}")
    if numero < 1:
        raise argparse.ArgumentTypeError("deve ser um inteiro >= 1")
    return numero


def monta_parser():
    parser = argparse.ArgumentParser(
        description="Conta linhas, palavras, caracteres e palavras mais frequentes de um arquivo de texto UTF-8."
    )
    parser.add_argument("arquivo", metavar="ARQUIVO", help="caminho para o arquivo de texto UTF-8")
    parser.add_argument("-l", "--linhas", action="store_true", help="contabiliza as linhas")
    parser.add_argument("-p", "--palavras", action="store_true", help="contabiliza as palavras")
    parser.add_argument("-c", "--chars", action="store_true", help="contabiliza os caracteres")
    parser.add_argument("--top", type=inteiro_positivo, metavar="N", help="lista as N palavras mais frequentes")
    parser.add_argument("--json", action="store_true", help="formata o resultado como JSON")
    parser.add_argument("-o", "--saida", metavar="CAMINHO", help="grava a saída no arquivo indicado")
    return parser


def top_palavras(conteudo, n):
    contagem = Counter()
    for token in conteudo.split():
        palavra = token.lower().strip(PONTUACAO)
        if palavra:
            contagem[palavra] += 1
    ordenadas = sorted(contagem.items(), key=lambda item: (-item[1], item[0]))
    return ordenadas[:n]


def formata_texto(resultado):
    linhas = []
    if "linhas" in resultado:
        linhas.append(f"Linhas: {resultado['linhas']}")
    if "palavras" in resultado:
        linhas.append(f"Palavras: {resultado['palavras']}")
    if "caracteres" in resultado:
        linhas.append(f"Caracteres: {resultado['caracteres']}")
    if "top_palavras" in resultado:
        linhas.append("Top Palavras:")
        linhas.extend(f"  - {palavra}: {ocorrencias}" for palavra, ocorrencias in resultado["top_palavras"])
    return "\n".join(linhas)


def formata_json(resultado):
    dados = {}
    for chave, valor in resultado.items():
        if chave == "top_palavras":
            valor = [{"palavra": palavra, "ocorrencias": ocorrencias} for palavra, ocorrencias in valor]
        dados[chave] = valor
    return json.dumps(dados, indent=2, ensure_ascii=False)


def main(argv=None):
    parser = monta_parser()
    args = parser.parse_args(argv)

    if not (args.linhas or args.palavras or args.chars or args.top is not None):
        args.linhas = args.palavras = args.chars = True

    try:
        if not os.path.exists(args.arquivo):
            print(f"Erro: arquivo não encontrado: {args.arquivo}", file=sys.stderr)
            return 1
        if not os.path.isfile(args.arquivo):
            print(f"Erro: o caminho não é um arquivo regular: {args.arquivo}", file=sys.stderr)
            return 1
        with open(args.arquivo, encoding="utf-8") as arquivo:
            conteudo = arquivo.read()
    except UnicodeDecodeError as exc:
        print(f"Erro ao ler arquivo: falha de decodificação UTF-8 ({exc})", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"Erro ao ler arquivo: {exc}", file=sys.stderr)
        return 1

    resultado = {}
    if args.linhas:
        resultado["linhas"] = len(conteudo.splitlines())
    if args.palavras:
        resultado["palavras"] = len(conteudo.split())
    if args.chars:
        resultado["caracteres"] = len(conteudo)
    if args.top is not None:
        resultado["top_palavras"] = top_palavras(conteudo, args.top)

    saida = formata_json(resultado) if args.json else formata_texto(resultado)

    if args.saida:
        try:
            os.makedirs(os.path.dirname(os.path.abspath(args.saida)), exist_ok=True)
            with open(args.saida, "w", encoding="utf-8") as destino:
                destino.write(saida + "\n")
        except OSError as exc:
            print(f"Erro ao gravar arquivo: {exc}", file=sys.stderr)
            return 1
        print(f"Salvo em {args.saida}")
    else:
        print(saida)
    return 0


if __name__ == "__main__":
    sys.exit(main())
