from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

COLUNAS_OBRIGATORIAS = (
    "data",
    "regiao",
    "produto",
    "quantidade",
    "preco_unitario",
    "status",
)


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Lê um CSV de vendas, agrega por região e grava o resumo em JSON."""
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    agregados: dict[str, dict] = {}
    linhas_invalidas = 0

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"', doublequote=True)
        header_raw = next(reader, None)
        if header_raw is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        header = [col.strip() for col in header_raw]
        indices = {nome: idx for idx, nome in enumerate(header)}

        faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in indices]
        if faltantes:
            raise ValueError(
                f"Colunas obrigatórias ausentes: {', '.join(faltantes)}"
            )

        num_colunas = len(header)
        idx_regiao = indices["regiao"]
        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_unitario"]
        idx_status = indices["status"]

        for row in reader:
            if not row:
                continue

            if len(row) != num_colunas:
                linhas_invalidas += 1
                continue

            valores = [v.strip() for v in row]
            regiao = valores[idx_regiao]
            produto = valores[idx_produto]
            qtd_str = valores[idx_quantidade]
            preco_str = valores[idx_preco]
            status = valores[idx_status]

            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(qtd_str)
            except ValueError:
                linhas_invalidas += 1
                continue

            if quantidade <= 0:
                linhas_invalidas += 1
                continue

            try:
                preco_unitario = float(preco_str)
            except ValueError:
                linhas_invalidas += 1
                continue

            if not math.isfinite(preco_unitario) or preco_unitario < 0:
                linhas_invalidas += 1
                continue

            if status.lower() != "concluida":
                continue

            if regiao not in agregados:
                agregados[regiao] = {
                    "quantidade_total": 0,
                    "total_vendas": 0.0,
                    "produtos": defaultdict(int),
                }

            dados_regiao = agregados[regiao]
            dados_regiao["quantidade_total"] += quantidade
            dados_regiao["total_vendas"] += quantidade * preco_unitario
            dados_regiao["produtos"][produto] += quantidade

    regioes: dict[str, dict] = {}
    for regiao in sorted(agregados.keys()):
        dados = agregados[regiao]
        total_vendas = float(round(dados["total_vendas"], 2))
        if total_vendas == 0.0:
            total_vendas = 0.0
        produto_mais_vendido = min(
            dados["produtos"].items(),
            key=lambda item: (-item[1], item[0]),
        )[0]
        regioes[regiao] = {
            "quantidade_total": int(dados["quantidade_total"]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(
        round(sum(r["total_vendas"] for r in regioes.values()), 2)
    )
    if total_geral == 0.0:
        total_geral = 0.0

    resultado = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado
