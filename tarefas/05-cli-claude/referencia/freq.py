#!/usr/bin/env python3
"""Conta as palavras mais frequentes de um arquivo de texto."""

import argparse
import json
import re
import sys
from collections import Counter
from collections.abc import Iterable

PALAVRA = re.compile(r"[^\W\d_]+")
EXIT_OK = 0
EXIT_ERRO_LEITURA = 1


def inteiro_positivo(valor: str) -> int:
    """Tipo para argparse: inteiro >= 1."""
    try:
        numero = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"inteiro inválido: {valor!r}") from None
    if numero < 1:
        raise argparse.ArgumentTypeError(f"deve ser >= 1: {numero}")
    return numero


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="freq", description="Mostra as palavras mais frequentes de um texto.")
    parser.add_argument("arquivo", metavar="ARQUIVO", help="arquivo de texto UTF-8 ('-' para stdin)")
    parser.add_argument("-n", "--top", type=inteiro_positivo, default=10, metavar="N",
                        help="quantidade de palavras exibidas (padrão: 10)")
    parser.add_argument("-m", "--min-len", type=inteiro_positivo, default=1, metavar="K",
                        help="tamanho mínimo da palavra (padrão: 1)")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="ignora maiúsculas/minúsculas")
    parser.add_argument("-x", "--excluir", action="append", default=[], metavar="PALAVRA",
                        help="palavra a ignorar (pode ser repetida)")
    parser.add_argument("--formato", choices=("texto", "json"), default="texto", help="formato de saída")
    return parser


def ler_texto(caminho: str) -> str:
    """Lê o arquivo (ou stdin, se ``-``) como UTF-8 estrito, independente do locale."""
    if caminho == "-":
        return sys.stdin.buffer.read().decode("utf-8")
    with open(caminho, encoding="utf-8") as arquivo:
        return arquivo.read()


def mais_frequentes(
    texto: str,
    top: int,
    min_len: int = 1,
    ignorar_caixa: bool = False,
    excluir: Iterable[str] = (),
) -> list[tuple[str, int]]:
    """Retorna até ``top`` pares (palavra, contagem) ordenados por contagem desc e palavra asc.

    As palavras são extraídas do texto original e só depois convertidas com
    ``str.lower()`` (converter o texto inteiro antes muda a extração: "İ".lower()
    gera um caractere combinante que não é letra).
    """
    palavras = PALAVRA.findall(texto)
    if ignorar_caixa:
        palavras = [p.lower() for p in palavras]
        excluir = [p.lower() for p in excluir]
    excluidas = set(excluir)
    contagem = Counter(p for p in palavras if len(p) >= min_len and p not in excluidas)
    return sorted(contagem.items(), key=lambda par: (-par[1], par[0]))[:top]


def formatar(resultado: list[tuple[str, int]], formato: str) -> str:
    if formato == "json":
        return json.dumps([{"palavra": p, "contagem": c} for p, c in resultado], ensure_ascii=False) + "\n"
    return "".join(f"{p}\t{c}\n" for p, c in resultado)


def main(argv: list[str] | None = None) -> int:
    args = criar_parser().parse_args(argv)
    try:
        texto = ler_texto(args.arquivo)
    except FileNotFoundError:
        print(f"erro: arquivo não encontrado: {args.arquivo}", file=sys.stderr)
        return EXIT_ERRO_LEITURA
    except UnicodeDecodeError:
        print(f"erro: arquivo não está em UTF-8: {args.arquivo}", file=sys.stderr)
        return EXIT_ERRO_LEITURA
    except OSError as exc:
        print(f"erro: não foi possível ler {args.arquivo}: {exc.strerror}", file=sys.stderr)
        return EXIT_ERRO_LEITURA

    resultado = mais_frequentes(texto, args.top, args.min_len, args.ignore_case, args.excluir)
    sys.stdout.write(formatar(resultado, args.formato))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
