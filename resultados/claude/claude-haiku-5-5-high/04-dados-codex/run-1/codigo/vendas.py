import contextlib
import csv
import json
import os
import re
import sys

COLUNAS_OBRIGATORIAS = ("produto", "quantidade", "preco_centavos", "status")
_INTEIRO = re.compile(r"[+-]?[0-9]+")


@contextlib.contextmanager
def _sem_limite_de_digitos():
    # Python 3.11 limita a conversão int<->str a 4300 dígitos; a aritmética exata não precisa disso.
    anterior = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(0)
    try:
        yield
    finally:
        sys.set_int_max_str_digits(anterior)


def _inteiro_nao_negativo(texto, campo):
    if not _INTEIRO.fullmatch(texto):
        raise ValueError(f"{campo} inválido: {texto!r}")
    valor = int(texto)
    if valor < 0:
        raise ValueError(f"{campo} não pode ser negativo: {texto!r}")
    return valor


def _campo(linha, nome):
    valor = linha[nome]
    if valor is None:
        raise ValueError(f"campo obrigatório faltando: {nome}")
    return valor


def _agregar_pagas(entrada):
    totais = {}
    with open(entrada, encoding="utf-8-sig", newline="") as arq:
        leitor = csv.DictReader(arq)
        cabecalho = leitor.fieldnames
        if not cabecalho:
            raise ValueError("arquivo sem cabeçalho")
        faltantes = [c for c in COLUNAS_OBRIGATORIAS if c not in cabecalho]
        if faltantes:
            raise ValueError(f"colunas obrigatórias faltando: {faltantes}")

        for linha in leitor:
            status = (linha["status"] or "").strip().lower()
            if status != "pago":
                continue

            produto = _campo(linha, "produto").strip()
            if not produto:
                raise ValueError("produto vazio")
            quantidade = _inteiro_nao_negativo(
                _campo(linha, "quantidade").strip(), "quantidade"
            )
            preco = _inteiro_nao_negativo(
                _campo(linha, "preco_centavos").strip(), "preco_centavos"
            )

            total = totais.setdefault(produto, [0, 0])
            total[0] += quantidade
            total[1] += quantidade * preco
    return totais


def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    if type(minimo_centavos) is not int or minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser int >= 0")
    if os.path.realpath(entrada) == os.path.realpath(saida):
        raise ValueError("entrada e saída devem ser arquivos distintos")

    with _sem_limite_de_digitos():
        totais = _agregar_pagas(entrada)
        resultado = [
            {"produto": produto, "quantidade": quantidade, "receita_centavos": receita}
            for produto, (quantidade, receita) in sorted(totais.items())
            if receita >= minimo_centavos
        ]
        texto = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"

    with open(saida, "w", encoding="utf-8", newline="") as arq:
        arq.write(texto)
    return resultado
