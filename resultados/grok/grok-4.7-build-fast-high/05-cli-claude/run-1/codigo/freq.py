#!/usr/bin/env python3
"""Conta as palavras mais frequentes de um arquivo de texto."""

import argparse
import json
import re
import sys
from collections import Counter

# Letras Unicode no texto original. Dígitos, "_" e pontuação separam palavras.
# Sem re.ASCII e sem normalização Unicode.
PALAVRA_RE = re.compile(r"[^\W\d_]+")


def inteiro_positivo(valor):
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError(f"inteiro invalido: {valor!r}")
    if numero < 1:
        raise argparse.ArgumentTypeError(f"valor deve ser >= 1: {numero}")
    return numero


def falhar(mensagem):
    linha = "erro: " + mensagem.replace("\r", " ").replace("\n", " ") + "\n"
    sys.stderr.buffer.write(linha.encode("utf-8", errors="backslashreplace"))
    sys.stderr.buffer.flush()
    raise SystemExit(1)


def ler_texto(caminho):
    if caminho == "-":
        origem = "entrada padrão"
        try:
            dados = sys.stdin.buffer.read()
        except OSError as exc:
            detalhe = exc.strerror or "erro de leitura"
            falhar(f"{origem}: {detalhe}")
    else:
        origem = caminho
        try:
            with open(caminho, "rb") as arquivo:
                dados = arquivo.read()
        except IsADirectoryError:
            falhar(f"{caminho}: é um diretório")
        except PermissionError:
            falhar(f"{caminho}: permissão negada")
        except FileNotFoundError:
            falhar(f"{caminho}: arquivo não encontrado")
        except OSError as exc:
            detalhe = exc.strerror or "erro de leitura"
            falhar(f"{caminho}: {detalhe}")
    try:
        return dados.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        falhar(f"{origem}: conteúdo não é UTF-8 válido")


def filtrar_palavras(texto, ignorar_caixa, minimo, excluidas):
    palavras = PALAVRA_RE.findall(texto)
    if ignorar_caixa:
        palavras = [palavra.lower() for palavra in palavras]
        bloqueadas = {palavra.lower() for palavra in excluidas}
    else:
        bloqueadas = set(excluidas)
    return [palavra for palavra in palavras if len(palavra) >= minimo and palavra not in bloqueadas]


def ordenar(contagens, limite):
    ranking = sorted(contagens.items(), key=lambda item: (-item[1], item[0]))
    return ranking[:limite]


def emitir(pares, formato):
    if formato == "json":
        payload = [{"palavra": palavra, "contagem": contagem} for palavra, contagem in pares]
        saida = json.dumps(payload, ensure_ascii=False) + "\n"
    elif pares:
        saida = "".join(f"{palavra}\t{contagem}\n" for palavra, contagem in pares)
    else:
        saida = ""
    sys.stdout.buffer.write(saida.encode("utf-8"))
    sys.stdout.buffer.flush()


def analisar_args(argv):
    parser = argparse.ArgumentParser(
        description="Conta as palavras mais frequentes de um arquivo de texto."
    )
    parser.add_argument(
        "arquivo",
        metavar="ARQUIVO",
        help="arquivo de texto em UTF-8, ou '-' para a entrada padrao",
    )
    parser.add_argument(
        "-n",
        "--top",
        type=inteiro_positivo,
        default=10,
        metavar="N",
        help="quantas palavras mostrar (padrao: 10)",
    )
    parser.add_argument(
        "-m",
        "--min-len",
        type=inteiro_positivo,
        default=1,
        metavar="K",
        help="ignora palavras com menos de K caracteres (padrao: 1)",
    )
    parser.add_argument(
        "-i",
        "--ignore-case",
        action="store_true",
        help="considera maiusculas e minusculas como a mesma palavra",
    )
    parser.add_argument(
        "-x",
        "--excluir",
        action="append",
        default=None,
        metavar="PALAVRA",
        help="ignora esta palavra; pode repetir a opcao",
    )
    parser.add_argument(
        "--formato",
        choices=("texto", "json"),
        default="texto",
        help="formato de saida (padrao: texto)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = analisar_args(argv)
    texto = ler_texto(args.arquivo)
    palavras = filtrar_palavras(
        texto,
        args.ignore_case,
        args.min_len,
        args.excluir or [],
    )
    emitir(ordenar(Counter(palavras), args.top), args.formato)
    return 0


if __name__ == "__main__":
    sys.exit(main())
