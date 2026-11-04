"""Agregação de vendas em CSV usando apenas a biblioteca padrão."""

import csv
import json
import math
import os
from pathlib import Path
import tempfile


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Leia as vendas, grave o resumo em JSON e retorne o mesmo resumo."""
    obrigatorias = (
        "data", "regiao", "produto", "quantidade", "preco_unitario", "status"
    )
    agregados = {}
    linhas_invalidas = 0

    with Path(entrada).open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("CSV sem cabeçalho obrigatório")
        cabecalho = [campo.strip() for campo in cabecalho]
        if any(coluna not in cabecalho for coluna in obrigatorias):
            raise ValueError("CSV sem todas as colunas obrigatórias")
        indices = {coluna: cabecalho.index(coluna) for coluna in obrigatorias}

        for campos in leitor:
            campos = [campo.strip() for campo in campos]
            if not any(campos):
                continue
            if len(campos) != len(cabecalho):
                linhas_invalidas += 1
                continue

            regiao = campos[indices["regiao"]]
            produto = campos[indices["produto"]]
            try:
                quantidade = int(campos[indices["quantidade"]])
                preco = float(campos[indices["preco_unitario"]])
            except ValueError:
                linhas_invalidas += 1
                continue
            if (not regiao or not produto or quantidade <= 0
                    or not math.isfinite(preco) or preco < 0):
                linhas_invalidas += 1
                continue
            if campos[indices["status"]].lower() != "concluida":
                continue

            if regiao not in agregados:
                agregados[regiao] = {
                    "quantidade": 0, "vendas": 0.0, "produtos": {}
                }
            agregado = agregados[regiao]
            agregado["quantidade"] += quantidade
            agregado["vendas"] += quantidade * preco
            produtos = agregado["produtos"]
            produtos[produto] = produtos.get(produto, 0) + quantidade

    regioes = {}
    for regiao in sorted(agregados):
        agregado = agregados[regiao]
        produtos = agregado["produtos"]
        regioes[regiao] = {
            "quantidade_total": agregado["quantidade"],
            "total_vendas": round(agregado["vendas"], 2),
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
    # Só substitua o destino depois de terminar a leitura e a gravação.
    temporario = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=destino.parent,
            delete=False, newline="\n"
        ) as arquivo:
            temporario = Path(arquivo.name)
            arquivo.write(conteudo)
        os.replace(temporario, destino)
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True)
    return resumo
