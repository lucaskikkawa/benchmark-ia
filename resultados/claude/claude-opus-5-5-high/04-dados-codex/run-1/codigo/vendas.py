import csv
import json
import re
import sys
from pathlib import Path

_COLUNAS = ("produto", "quantidade", "preco_centavos", "status")
_INTEIRO = re.compile(r"[+-]?[0-9]+")


def _inteiro_nao_negativo(texto, coluna):
    if texto is None:
        raise ValueError(f"campo obrigatório ausente: {coluna}")
    valor = texto.strip()
    if not _INTEIRO.fullmatch(valor):
        raise ValueError(f"valor inválido em {coluna}: {texto!r}")
    numero = int(valor)
    if numero < 0:
        raise ValueError(f"valor negativo em {coluna}: {texto!r}")
    return numero


def _processar(entrada, minimo_centavos):
    with open(entrada, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("arquivo vazio: cabeçalho ausente")
        faltando = [c for c in _COLUNAS if c not in cabecalho]
        if faltando:
            raise ValueError(f"colunas obrigatórias ausentes: {', '.join(faltando)}")
        i_prod, i_qtd, i_preco, i_status = (cabecalho.index(c) for c in _COLUNAS)

        totais = {}
        for linha in leitor:
            n = len(linha)
            if i_status >= n or linha[i_status].strip().lower() != "pago":
                continue
            if i_prod >= n:
                raise ValueError("campo obrigatório ausente: produto")
            produto = linha[i_prod].strip()
            if not produto:
                raise ValueError("produto vazio")
            quantidade = _inteiro_nao_negativo(
                linha[i_qtd] if i_qtd < n else None, "quantidade"
            )
            preco = _inteiro_nao_negativo(
                linha[i_preco] if i_preco < n else None, "preco_centavos"
            )
            atual = totais.get(produto)
            if atual is None:
                totais[produto] = [quantidade, quantidade * preco]
            else:
                atual[0] += quantidade
                atual[1] += quantidade * preco

    return [
        {"produto": p, "quantidade": q, "receita_centavos": r}
        for p, (q, r) in sorted(totais.items())
        if r >= minimo_centavos
    ]


def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    if type(minimo_centavos) is not int:
        raise ValueError("minimo_centavos deve ser int")
    if minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser >= 0")

    # Permite inteiros arbitrariamente grandes e campos longos sem limites
    # globais do interpretador; restaura as configurações ao final.
    limite_digitos = sys.get_int_max_str_digits()
    limite_campo = csv.field_size_limit()
    sys.set_int_max_str_digits(0)
    csv.field_size_limit(sys.maxsize)
    try:
        resultado = _processar(entrada, minimo_centavos)
        texto = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    finally:
        sys.set_int_max_str_digits(limite_digitos)
        csv.field_size_limit(limite_campo)

    Path(saida).write_text(texto, encoding="utf-8", newline="")
    return resultado
