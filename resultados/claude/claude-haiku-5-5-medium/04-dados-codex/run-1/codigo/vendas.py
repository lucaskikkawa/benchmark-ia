import csv
import json
import re
import sys
from pathlib import Path

COLUNAS_OBRIGATORIAS = ("produto", "quantidade", "preco_centavos", "status")
_INTEIRO = re.compile(r"[+-]?[0-9]+")


def _inteiro_nao_negativo(valor):
    if valor is None:
        raise ValueError("campo numérico obrigatório ausente")
    texto = valor.strip()
    if not _INTEIRO.fullmatch(texto):
        raise ValueError(f"inteiro inválido: {valor!r}")
    numero = int(texto)
    if numero < 0:
        raise ValueError(f"valor negativo: {valor!r}")
    return numero


def _ler_totais(entrada):
    totais = {}
    with open(entrada, newline="", encoding="utf-8-sig") as arquivo:
        leitor = csv.DictReader(arquivo)
        colunas = leitor.fieldnames
        if colunas is None:
            raise ValueError("arquivo sem cabeçalho")
        faltantes = [c for c in COLUNAS_OBRIGATORIAS if c not in colunas]
        if faltantes:
            raise ValueError(f"colunas obrigatórias ausentes: {faltantes}")

        for linha in leitor:
            if (linha.get("status") or "").strip().lower() != "pago":
                continue

            produto = linha.get("produto")
            produto = produto.strip() if produto is not None else ""
            if not produto:
                raise ValueError("produto vazio ou ausente em linha paga")
            quantidade = _inteiro_nao_negativo(linha.get("quantidade"))
            preco = _inteiro_nao_negativo(linha.get("preco_centavos"))

            qtd_acumulada, receita_acumulada = totais.get(produto, (0, 0))
            totais[produto] = (
                qtd_acumulada + quantidade,
                receita_acumulada + quantidade * preco,
            )
    return totais


def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    if type(minimo_centavos) is not int or minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser int >= 0")
    if Path(entrada).resolve() == Path(saida).resolve():
        raise ValueError("entrada e saída devem ser arquivos distintos")

    # Permite inteiros com mais de 4300 dígitos, mantendo a aritmética exata.
    limite_digitos = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(0)
    try:
        totais = _ler_totais(entrada)
        resultado = [
            {"produto": produto, "quantidade": quantidade, "receita_centavos": receita}
            for produto, (quantidade, receita) in sorted(totais.items())
            if receita >= minimo_centavos
        ]
        # Só grava depois de tudo validado, para não corromper a saída anterior.
        texto = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    finally:
        sys.set_int_max_str_digits(limite_digitos)

    with open(saida, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)
    return resultado
