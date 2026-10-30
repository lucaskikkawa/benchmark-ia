"""Resume vendas de um CSV e grava o resultado em JSON."""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path

COLUNAS_OBRIGATORIAS = (
    "data",
    "regiao",
    "produto",
    "quantidade",
    "preco_unitario",
    "status",
)


def _linha_totalmente_vazia(row: list[str]) -> bool:
    return all(not campo.strip() for campo in row)


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    with entrada_path.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)

        cabecalho: list[str] | None = None
        for row in leitor:
            if _linha_totalmente_vazia(row):
                continue
            cabecalho = row
            break
        if cabecalho is None:
            raise ValueError("CSV sem cabeçalho ou sem colunas obrigatórias")

        nomes = [coluna.strip() for coluna in cabecalho]
        indices: dict[str, int] = {}
        for i, nome in enumerate(nomes):
            indices.setdefault(nome, i)

        faltando = [coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in indices]
        if faltando:
            raise ValueError("Colunas obrigatórias ausentes: " + ", ".join(faltando))

        n_colunas = len(cabecalho)
        idx_regiao = indices["regiao"]
        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_unitario"]
        idx_status = indices["status"]

        quantidades: dict[str, dict[str, int]] = {}
        totais: dict[str, float] = {}
        linhas_invalidas = 0

        for row in leitor:
            if _linha_totalmente_vazia(row):
                continue
            if len(row) != n_colunas:
                linhas_invalidas += 1
                continue

            regiao = row[idx_regiao].strip()
            produto = row[idx_produto].strip()
            quantidade_txt = row[idx_quantidade].strip()
            preco_txt = row[idx_preco].strip()
            status = row[idx_status].strip()

            if not regiao or not produto:
                linhas_invalidas += 1
                continue
            try:
                quantidade = int(quantidade_txt)
            except (ValueError, TypeError):
                linhas_invalidas += 1
                continue
            if quantidade <= 0:
                linhas_invalidas += 1
                continue
            try:
                preco = float(preco_txt)
            except (ValueError, TypeError):
                linhas_invalidas += 1
                continue
            if not math.isfinite(preco) or preco < 0:
                linhas_invalidas += 1
                continue
            if status.lower() != "concluida":
                continue

            por_produto = quantidades.setdefault(regiao, {})
            por_produto[produto] = por_produto.get(produto, 0) + quantidade
            totais[regiao] = totais.get(regiao, 0.0) + quantidade * preco

    regioes: dict[str, dict] = {}
    for regiao in sorted(quantidades):
        por_produto = quantidades[regiao]
        produto_mais_vendido = min(
            por_produto, key=lambda nome: (-por_produto[nome], nome)
        )
        regioes[regiao] = {
            "quantidade_total": int(sum(por_produto.values())),
            "total_vendas": float(round(totais[regiao], 2)),
            "produto_mais_vendido": produto_mais_vendido,
        }

    resultado = {
        "regioes": regioes,
        "total_geral": float(
            round(sum(item["total_vendas"] for item in regioes.values()), 2)
        ),
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as arquivo:
        json.dump(resultado, arquivo, ensure_ascii=False, indent=2)

    return resultado
