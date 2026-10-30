"""Contador de palavras pela linha de comando."""

import argparse
import json
import sys
from collections import Counter


def _inteiro_positivo(valor: str) -> int:
    try:
        numero = int(valor)
    except (TypeError, ValueError):
        raise argparse.ArgumentTypeError("inteiro positivo esperado") from None
    if numero <= 0:
        raise argparse.ArgumentTypeError("inteiro positivo esperado")
    return numero


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Conta palavras de um arquivo de texto UTF-8.",
        allow_abbrev=False,
    )
    parser.add_argument("arquivo", help="arquivo UTF-8 a ser contado")
    parser.add_argument(
        "--minimo",
        type=_inteiro_positivo,
        default=1,
        help="exibe somente tokens com contagem maior ou igual a N (padrão: 1)",
    )
    parser.add_argument(
        "--top",
        type=_inteiro_positivo,
        default=None,
        help="limita a N resultados depois de filtrar e ordenar",
    )
    parser.add_argument(
        "--ignorar-caixa",
        action="store_true",
        help="aplica str.casefold() antes de contar",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="escreve uma lista JSON de objetos palavra/contagem",
    )
    return parser


def _erro(mensagem: str) -> int:
    print(mensagem, file=sys.stderr)
    return 2


def _codigo_saida(exc: SystemExit) -> int:
    codigo = exc.code
    if codigo is None:
        return 0
    if isinstance(codigo, int):
        return codigo
    return 2


def main(argv=None) -> int:
    """Conta palavras de um arquivo. Retorna 0 em sucesso e 2 em erro."""
    parser = _parser()
    try:
        args = parser.parse_args(argv)
    except SystemExit as exc:
        return _codigo_saida(exc)

    try:
        with open(args.arquivo, encoding="utf-8") as arquivo:
            texto = arquivo.read()
    except UnicodeError:
        return _erro("erro: UTF-8 invalido")
    except OSError:
        return _erro("erro: arquivo ausente ou ilegivel")

    tokens = texto.split()
    if args.ignorar_caixa:
        tokens = [token.casefold() for token in tokens]

    contagens = Counter(tokens)
    resultados = [
        (palavra, contagem)
        for palavra, contagem in contagens.items()
        if contagem >= args.minimo
    ]
    resultados.sort(key=lambda item: (-item[1], item[0]))
    if args.top is not None:
        resultados = resultados[: args.top]

    if args.json:
        payload = [
            {"palavra": palavra, "contagem": contagem}
            for palavra, contagem in resultados
        ]
        sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    else:
        for palavra, contagem in resultados:
            sys.stdout.write(f"{palavra}\t{contagem}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
