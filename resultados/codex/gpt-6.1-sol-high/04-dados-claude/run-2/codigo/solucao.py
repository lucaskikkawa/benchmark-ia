"""Agregação de vendas de um CSV em um resumo JSON."""

import csv
import json
import math
import os
import tempfile
from pathlib import Path


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Leia as vendas, grave o resumo em UTF-8 e retorne o mesmo resumo."""
    obrigatorias = (
        "data", "regiao", "produto", "quantidade", "preco_unitario", "status"
    )
    acumulados = {}
    linhas_invalidas = 0

    with Path(entrada).open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("CSV sem cabeçalho")
        cabecalho = [campo.strip() for campo in cabecalho]
        if not set(obrigatorias).issubset(cabecalho):
            raise ValueError("Faltam colunas obrigatórias no CSV")
        indices = {nome: cabecalho.index(nome) for nome in obrigatorias}

        for linha in leitor:
            linha = [valor.strip() for valor in linha]
            if not any(linha):
                continue
            if len(linha) != len(cabecalho):
                linhas_invalidas += 1
                continue

            regiao = linha[indices["regiao"]]
            produto = linha[indices["produto"]]
            try:
                quantidade = int(linha[indices["quantidade"]])
                preco = float(linha[indices["preco_unitario"]])
            except ValueError:
                linhas_invalidas += 1
                continue
            if (not regiao or not produto or quantidade <= 0
                    or not math.isfinite(preco) or preco < 0):
                linhas_invalidas += 1
                continue
            if linha[indices["status"]].lower() != "concluida":
                continue

            if regiao not in acumulados:
                acumulados[regiao] = {
                    "quantidade": 0, "vendas": 0.0, "produtos": {}
                }
            acumulado = acumulados[regiao]
            acumulado["quantidade"] += quantidade
            acumulado["vendas"] += quantidade * preco
            produtos = acumulado["produtos"]
            produtos[produto] = produtos.get(produto, 0) + quantidade

    regioes = {}
    for regiao in sorted(acumulados):
        acumulado = acumulados[regiao]
        produtos = acumulado["produtos"]
        regioes[regiao] = {
            "quantidade_total": acumulado["quantidade"],
            "total_vendas": round(acumulado["vendas"], 2),
            "produto_mais_vendido": min(
                produtos, key=lambda produto: (-produtos[produto], produto)
            ),
        }

    resumo = {
        "regioes": regioes,
        "total_geral": round(sum(
            (regiao["total_vendas"] for regiao in regioes.values()), 0.0
        ), 2),
        "linhas_invalidas": linhas_invalidas,
    }
    conteudo = json.dumps(resumo, ensure_ascii=False, indent=2)
    destino = Path(saida)
    destino.parent.mkdir(parents=True, exist_ok=True)

    # Só substitua a saída após a escrita completa do arquivo temporário.
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="", dir=destino.parent,
            prefix=".resumo-", suffix=".tmp", delete=False
        ) as arquivo:
            temporario = Path(arquivo.name)
            arquivo.write(conteudo)
        os.replace(temporario, destino)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)

    return resumo
