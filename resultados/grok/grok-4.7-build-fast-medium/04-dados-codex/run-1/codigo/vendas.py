"""Resumo de vendas pagas a partir de um CSV."""

import csv
import json
import re

_INTEIRO = re.compile(r"[+-]?[0-9]+\Z")
_COLUNAS = ("produto", "quantidade", "preco_centavos", "status")


def _inteiro_nao_negativo(texto: str) -> int:
    valor_texto = texto.strip()
    if _INTEIRO.fullmatch(valor_texto) is None:
        raise ValueError("número inválido")
    valor = int(valor_texto)
    if valor < 0:
        raise ValueError("número negativo")
    return valor


def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    if type(minimo_centavos) is not int or minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser int >= 0")

    agregados: dict[str, list[int]] = {}

    with open(entrada, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        cabecalho = leitor.fieldnames
        if not cabecalho or any(coluna not in cabecalho for coluna in _COLUNAS):
            raise ValueError("cabeçalho sem coluna obrigatória")

        for linha in leitor:
            status = linha.get("status")
            if not isinstance(status, str) or status.strip().lower() != "pago":
                continue

            produto = linha.get("produto")
            quantidade_txt = linha.get("quantidade")
            preco_txt = linha.get("preco_centavos")
            if (
                not isinstance(produto, str)
                or not isinstance(quantidade_txt, str)
                or not isinstance(preco_txt, str)
            ):
                raise ValueError("campo obrigatório ausente em linha paga")

            nome = produto.strip()
            if nome == "":
                raise ValueError("produto vazio")

            quantidade = _inteiro_nao_negativo(quantidade_txt)
            preco = _inteiro_nao_negativo(preco_txt)
            acumulado = agregados.get(nome)
            if acumulado is None:
                agregados[nome] = [quantidade, quantidade * preco]
            else:
                acumulado[0] += quantidade
                acumulado[1] += quantidade * preco

    resumo = [
        {
            "produto": nome,
            "quantidade": totais[0],
            "receita_centavos": totais[1],
        }
        for nome, totais in agregados.items()
        if totais[1] >= minimo_centavos
    ]
    resumo.sort(key=lambda item: item["produto"])

    conteudo = json.dumps(resumo, ensure_ascii=False) + "\n"
    with open(saida, "wb") as destino:
        destino.write(conteudo.encode("utf-8"))
    return resumo
