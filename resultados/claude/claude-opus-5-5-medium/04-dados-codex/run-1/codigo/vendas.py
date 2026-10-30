"""Resumo de vendas pagas de um CSV em JSON."""

import csv
import json
import re
import sys

_COLUNAS = ("produto", "quantidade", "preco_centavos", "status")
_INTEIRO = re.compile(r"[+-]?[0-9]+\Z", re.ASCII)


def _inteiro_nao_negativo(texto, campo, linha):
    valor = texto.strip()
    if not _INTEIRO.match(valor):
        raise ValueError(f"linha {linha}: {campo} inválido: {texto!r}")
    sinal = -1 if valor[0] == "-" else 1
    digitos = valor.lstrip("+-").lstrip("0") or "0"
    numero = sinal * int(digitos)
    if numero < 0:
        raise ValueError(f"linha {linha}: {campo} negativo: {texto!r}")
    return numero


def _resumir(entrada, saida, minimo_centavos):
    if type(minimo_centavos) is not int:
        raise ValueError("minimo_centavos deve ser int")
    if minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser >= 0")

    with open(entrada, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("CSV sem cabeçalho")
        nomes = [nome.strip() for nome in cabecalho]
        indices = {}
        for coluna in _COLUNAS:
            if coluna not in nomes:
                raise ValueError(f"coluna obrigatória ausente: {coluna}")
            indices[coluna] = nomes.index(coluna)
        i_prod = indices["produto"]
        i_qtd = indices["quantidade"]
        i_preco = indices["preco_centavos"]
        i_status = indices["status"]
        maximo = max(indices.values())

        totais = {}
        for registro in leitor:
            if len(registro) <= i_status:
                continue
            if registro[i_status].strip().lower() != "pago":
                continue
            linha = leitor.line_num
            if len(registro) <= maximo:
                raise ValueError(f"linha {linha}: campos obrigatórios faltando")
            produto = registro[i_prod].strip()
            if not produto:
                raise ValueError(f"linha {linha}: produto vazio")
            quantidade = _inteiro_nao_negativo(registro[i_qtd], "quantidade", linha)
            preco = _inteiro_nao_negativo(registro[i_preco], "preco_centavos", linha)
            atual = totais.get(produto)
            if atual is None:
                totais[produto] = [quantidade, quantidade * preco]
            else:
                atual[0] += quantidade
                atual[1] += quantidade * preco

    resultado = [
        {"produto": produto, "quantidade": qtd, "receita_centavos": receita}
        for produto, (qtd, receita) in sorted(totais.items())
        if receita >= minimo_centavos
    ]
    conteudo = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"

    with open(saida, "w", encoding="utf-8", newline="") as arquivo:
        arquivo.write(conteudo)
    return resultado


def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    # Permite inteiros exatos de qualquer tamanho na conversão texto <-> int.
    limite = getattr(sys, "get_int_max_str_digits", None)
    if limite is None:
        return _resumir(entrada, saida, minimo_centavos)
    anterior = sys.get_int_max_str_digits()
    sys.set_int_max_str_digits(0)
    try:
        return _resumir(entrada, saida, minimo_centavos)
    finally:
        sys.set_int_max_str_digits(anterior)
