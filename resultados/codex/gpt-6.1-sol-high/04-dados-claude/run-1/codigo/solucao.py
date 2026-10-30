"""Leitura e agregação de vendas em CSV usando a biblioteca padrão."""

import csv
import json
import math
import os
from pathlib import Path
import tempfile


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Grava e retorna o resumo, preservando a saída se ocorrer um erro."""
    obrigatorias = (
        "data", "regiao", "produto", "quantidade", "preco_unitario", "status"
    )
    acumulados = {}
    linhas_invalidas = 0

    with Path(entrada).open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, [])
        cabecalho = [coluna.strip() for coluna in cabecalho]
        if not set(obrigatorias).issubset(cabecalho):
            raise ValueError("O CSV não contém todas as colunas obrigatórias.")
        indices = {nome: cabecalho.index(nome) for nome in obrigatorias}

        for campos in leitor:
            campos = [valor.strip() for valor in campos]
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
            if not regiao or not produto or quantidade <= 0 or not math.isfinite(preco) or preco < 0:
                linhas_invalidas += 1
                continue
            if campos[indices["status"]].lower() != "concluida":
                continue

            if regiao not in acumulados:
                acumulados[regiao] = {"quantidade": 0, "total": 0.0, "produtos": {}}
            grupo = acumulados[regiao]
            grupo["quantidade"] += quantidade
            grupo["total"] += quantidade * preco
            produtos = grupo["produtos"]
            produtos[produto] = produtos.get(produto, 0) + quantidade

    regioes = {}
    for regiao in sorted(acumulados):
        grupo = acumulados[regiao]
        produtos = grupo["produtos"]
        regioes[regiao] = {
            "quantidade_total": grupo["quantidade"],
            "total_vendas": round(grupo["total"], 2),
            "produto_mais_vendido": min(produtos, key=lambda nome: (-produtos[nome], nome)),
        }
    resumo = {
        "regioes": regioes,
        "total_geral": round(sum((grupo["total_vendas"] for grupo in regioes.values()), 0.0), 2),
        "linhas_invalidas": linhas_invalidas,
    }

    # Escreve em um arquivo temporário para só substituir a saída após o sucesso.
    destino = Path(saida)
    conteudo = json.dumps(resumo, ensure_ascii=False, indent=2)
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
        if temporario is not None and temporario.exists():
            temporario.unlink()
    return resumo
