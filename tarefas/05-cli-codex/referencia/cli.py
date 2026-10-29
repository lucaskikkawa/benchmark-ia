import argparse
from collections import Counter
import json
from pathlib import Path


def inteiro_positivo(texto):
    valor = int(texto)
    if valor < 1:
        raise argparse.ArgumentTypeError("o mínimo deve ser positivo")
    return valor


def main(argv=None) -> int:
    """Conte tokens de um arquivo e emita texto tabulado ou JSON."""
    parser = argparse.ArgumentParser(description="Conte palavras separadas por espaços.")
    parser.add_argument('arquivo', type=Path)
    parser.add_argument('--minimo', type=inteiro_positivo, default=1)
    parser.add_argument('--top', type=inteiro_positivo, default=None)
    parser.add_argument('--ignorar-caixa', action='store_true')
    parser.add_argument('--json', action='store_true', dest='como_json')
    args = parser.parse_args(argv)
    try:
        texto = args.arquivo.read_text(encoding='utf-8')
    except (OSError, UnicodeError) as erro:
        parser.error(f"não foi possível ler o arquivo: {erro}")
    palavras = texto.split()
    if args.ignorar_caixa:
        palavras = [palavra.casefold() for palavra in palavras]
    contagens = Counter(palavras)
    ordenadas = sorted(((p, n) for p, n in contagens.items() if n >= args.minimo),
                       key=lambda item: (-item[1], item[0]))
    if args.top is not None:
        ordenadas = ordenadas[:args.top]
    if args.como_json:
        print(json.dumps([{'palavra': p, 'contagem': n} for p, n in ordenadas], ensure_ascii=False))
    else:
        for palavra, contagem in ordenadas:
            print(f"{palavra}\t{contagem}")
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
