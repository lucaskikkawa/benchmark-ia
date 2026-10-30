#!/usr/bin/env python3
"""Conta as palavras mais frequentes de um arquivo de texto UTF-8."""

import argparse
import json
import re
import sys
from collections import Counter

# Letras Unicode: dígitos, "_" e pontuação separam palavras. Sem normalização.
WORD_RE = re.compile(r"[^\W\d_]+")


def inteiro_positivo(valor: str) -> int:
    try:
        numero = int(valor)
    except ValueError:
        raise argparse.ArgumentTypeError(
            f"inteiro inválido: {valor!r}"
        ) from None
    if numero < 1:
        raise argparse.ArgumentTypeError(f"deve ser um inteiro >= 1: {numero}")
    return numero


def criar_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Conta as palavras mais frequentes de um arquivo de texto."
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="caminho do arquivo UTF-8; '-' lê da entrada padrão",
    )
    parser.add_argument(
        "-n",
        "--top",
        type=inteiro_positivo,
        default=10,
        metavar="N",
        help="quantas palavras mostrar (padrão: 10)",
    )
    parser.add_argument(
        "-m",
        "--min-len",
        type=inteiro_positivo,
        default=1,
        metavar="K",
        help="ignora palavras com menos de K caracteres (padrão: 1)",
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="converte as palavras para minúsculas antes de contar",
    )
    parser.add_argument(
        "-x",
        "--excluir",
        action="append",
        default=None,
        metavar="PALAVRA",
        help="ignora esta palavra; pode ser repetida",
    )
    parser.add_argument(
        "--formato",
        choices=("texto", "json"),
        default="texto",
        help="formato de saída (padrão: texto)",
    )
    return parser


def escrever(stream, texto: str) -> None:
    """Escreve UTF-8 sem depender da codificação do terminal."""
    dados = texto.encode("utf-8")
    buffer = getattr(stream, "buffer", None)
    if buffer is not None:
        buffer.write(dados)
    else:
        stream.write(texto)


def erro(mensagem: str) -> None:
    escrever(sys.stderr, f"erro: {mensagem}\n")
    raise SystemExit(1)


def ler_texto(caminho: str) -> str:
    try:
        if caminho == "-":
            dados = sys.stdin.buffer.read()
        else:
            with open(caminho, "rb") as arquivo:
                dados = arquivo.read()
    except IsADirectoryError:
        erro(f"é um diretório: {caminho}")
    except FileNotFoundError:
        erro(f"arquivo não encontrado: {caminho}")
    except PermissionError:
        erro(f"permissão negada: {caminho}")
    except OSError as exc:
        detalhe = exc.strerror or "falha de leitura"
        erro(f"não foi possível ler: {caminho}: {detalhe}")

    try:
        return dados.decode("utf-8")
    except UnicodeDecodeError:
        erro("conteúdo não é UTF-8 válido")


def frequencias(texto: str, *, ignorar_caixa: bool, minimo: int, excluir: list[str]):
    palavras = WORD_RE.findall(texto)
    if ignorar_caixa:
        palavras = [palavra.lower() for palavra in palavras]
        ignoradas = {palavra.lower() for palavra in excluir}
    else:
        ignoradas = set(excluir)

    contagem = Counter(
        palavra
        for palavra in palavras
        if len(palavra) >= minimo and palavra not in ignoradas
    )
    ordenadas = sorted(contagem.items(), key=lambda item: (-item[1], item[0]))
    return ordenadas


def formatar(ordenadas, formato: str, limite: int) -> str:
    selecionadas = ordenadas[:limite]
    if formato == "json":
        payload = [
            {"palavra": palavra, "contagem": contagem}
            for palavra, contagem in selecionadas
        ]
        return json.dumps(payload, ensure_ascii=False) + "\n"
    if not selecionadas:
        return ""
    return "".join(f"{palavra}\t{contagem}\n" for palavra, contagem in selecionadas)


def main(argv=None) -> int:
    args = criar_parser().parse_args(argv)
    texto = ler_texto(args.arquivo)
    ordenadas = frequencias(
        texto,
        ignorar_caixa=args.ignore_case,
        minimo=args.min_len,
        excluir=args.excluir or [],
    )
    escrever(sys.stdout, formatar(ordenadas, args.formato, args.top))
    return 0


if __name__ == "__main__":
    sys.exit(main())
