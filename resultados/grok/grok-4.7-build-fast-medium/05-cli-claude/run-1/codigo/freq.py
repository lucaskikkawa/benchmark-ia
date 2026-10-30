#!/usr/bin/env python3
"""Conta as palavras mais frequentes de um arquivo de texto."""

import argparse
import json
import re
import sys

# Letras Unicode: \W inclui dígitos e "_", então a negação deixa só letras.
_PALAVRA = re.compile(r"[^\W\d_]+")


def inteiro_minimo_1(valor):
    try:
        numero = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(f"inteiro inválido: {valor!r}")
    if numero < 1:
        raise argparse.ArgumentTypeError(f"deve ser >= 1: {valor!r}")
    return numero


def _escrever(stream, texto):
    """Escreve texto em UTF-8, sem depender da codificação do terminal."""
    dados = texto.encode("utf-8", "backslashreplace")
    buffer = getattr(stream, "buffer", None)
    if buffer is not None:
        buffer.write(dados)
    else:
        stream.write(dados.decode("utf-8"))


def ler_texto(caminho):
    """Lê o arquivo (ou stdin se caminho for '-') como UTF-8 estrito."""
    try:
        if caminho == "-":
            dados = sys.stdin.buffer.read()
        else:
            with open(caminho, "rb") as arquivo:
                dados = arquivo.read()
        return dados.decode("utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        detalhe = str(exc).replace("\r", " ").replace("\n", " ")
        _escrever(sys.stderr, f"erro: {detalhe}\n")
        sys.exit(1)


def contar(texto, min_len, ignorar_caixa, excluir):
    palavras = _PALAVRA.findall(texto)
    if ignorar_caixa:
        palavras = [palavra.lower() for palavra in palavras]
        excluir = {item.lower() for item in excluir}
    else:
        excluir = set(excluir)

    frequencias = {}
    for palavra in palavras:
        if len(palavra) < min_len or palavra in excluir:
            continue
        frequencias[palavra] = frequencias.get(palavra, 0) + 1

    ordenadas = sorted(frequencias.items(), key=lambda item: (-item[1], item[0]))
    return ordenadas


def emitir(pares, formato, top):
    pares = pares[:top]
    if formato == "json":
        payload = [{"palavra": palavra, "contagem": contagem} for palavra, contagem in pares]
        _escrever(sys.stdout, json.dumps(payload, ensure_ascii=False) + "\n")
        return
    linhas = "".join(f"{palavra}\t{contagem}\n" for palavra, contagem in pares)
    _escrever(sys.stdout, linhas)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Conta as palavras mais frequentes de um texto.")
    parser.add_argument("arquivo", metavar="ARQUIVO", help="arquivo UTF-8, ou '-' para a entrada padrão")
    parser.add_argument("-n", "--top", type=inteiro_minimo_1, default=10, metavar="N", help="quantas palavras mostrar (padrão: 10)")
    parser.add_argument("-m", "--min-len", type=inteiro_minimo_1, default=1, metavar="K", help="tamanho mínimo da palavra (padrão: 1)")
    parser.add_argument("-i", "--ignore-case", action="store_true", help="conta sem distinguir maiúsculas de minúsculas")
    parser.add_argument("-x", "--excluir", action="append", default=[], metavar="PALAVRA", help="ignora esta palavra; pode ser repetida")
    parser.add_argument("--formato", choices=("texto", "json"), default="texto", help="formato de saída (padrão: texto)")
    args = parser.parse_args(argv)

    texto = ler_texto(args.arquivo)
    pares = contar(texto, args.min_len, args.ignore_case, args.excluir)
    emitir(pares, args.formato, args.top)
    return 0


if __name__ == "__main__":
    sys.exit(main())
