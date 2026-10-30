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
    agregados = {}
    linhas_invalidas = 0

    with Path(entrada).open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("CSV sem cabeçalho")
        cabecalho = [campo.strip() for campo in cabecalho]
        if any(coluna not in cabecalho for coluna in obrigatorias):
            raise ValueError("Faltam colunas obrigatórias no cabeçalho")
        indices = {coluna: cabecalho.index(coluna) for coluna in obrigatorias}

        for linha in leitor:
            valores = [valor.strip() for valor in linha]
            if not any(valores):
                continue
            if len(valores) != len(cabecalho):
                linhas_invalidas += 1
                continue

            regiao = valores[indices["regiao"]]
            produto = valores[indices["produto"]]
            try:
                quantidade = int(valores[indices["quantidade"]])
                preco = float(valores[indices["preco_unitario"]])
            except ValueError:
                linhas_invalidas += 1
                continue
            if (not regiao or not produto or quantidade <= 0
                    or not math.isfinite(preco) or preco < 0):
                linhas_invalidas += 1
                continue
            if valores[indices["status"]].lower() != "concluida":
                continue

            if regiao not in agregados:
                agregados[regiao] = {"quantidade": 0, "total": 0.0, "produtos": {}}
            agregado = agregados[regiao]
            agregado["quantidade"] += quantidade
            agregado["total"] += quantidade * preco
            produtos = agregado["produtos"]
            produtos[produto] = produtos.get(produto, 0) + quantidade

    regioes = {}
    for regiao in sorted(agregados):
        agregado = agregados[regiao]
        produtos = agregado["produtos"]
        regioes[regiao] = {
            "quantidade_total": agregado["quantidade"],
            "total_vendas": round(agregado["total"], 2),
            "produto_mais_vendido": min(produtos, key=lambda p: (-produtos[p], p)),
        }
    resumo = {
        "regioes": regioes,
        "total_geral": round(sum((r["total_vendas"] for r in regioes.values()), 0.0), 2),
        "linhas_invalidas": linhas_invalidas,
    }

    # Prepare tudo antes de tocar na saída e substitua-a somente após a gravação.
    conteudo = json.dumps(resumo, ensure_ascii=False, indent=2)
    destino = Path(saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destino.parent, delete=False
        ) as arquivo:
            temporario = Path(arquivo.name)
            arquivo.write(conteudo)
        os.replace(temporario, destino)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)
    return resumo
