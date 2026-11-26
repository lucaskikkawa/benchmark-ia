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
    """Lê um CSV de vendas, agrega por região, escreve o resumo em JSON e o retorna."""
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        nomes_cabecalho = [coluna.strip() for coluna in cabecalho]
        indices: dict[str, int] = {}
        for idx, nome in enumerate(nomes_cabecalho):
            if nome not in indices:
                indices[nome] = idx

        faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in indices]
        if faltantes:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

        num_colunas = len(cabecalho)
        idx_regiao = indices["regiao"]
        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_unitario"]
        idx_status = indices["status"]

        linhas_invalidas = 0
        quantidades_por_regiao: dict[str, int] = defaultdict(int)
        totais_por_regiao: dict[str, float] = defaultdict(float)
        produtos_por_regiao: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        for linha in leitor:
            valores = [valor.strip() for valor in linha]
            if not any(valores):
                continue

            if len(valores) != num_colunas:
                linhas_invalidas += 1
                continue

            regiao = valores[idx_regiao]
            produto = valores[idx_produto]
            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(valores[idx_quantidade])
            except ValueError:
                linhas_invalidas += 1
                continue

            if quantidade <= 0:
                linhas_invalidas += 1
                continue

            try:
                preco_unitario = float(valores[idx_preco])
            except ValueError:
                linhas_invalidas += 1
                continue

            if not math.isfinite(preco_unitario) or preco_unitario < 0:
                linhas_invalidas += 1
                continue

            if valores[idx_status].lower() != "concluida":
                continue

            quantidades_por_regiao[regiao] += quantidade
            totais_por_regiao[regiao] += quantidade * preco_unitario
            produtos_por_regiao[regiao][produto] += quantidade

    regioes: dict[str, dict[str, int | float | str]] = {}
    soma_total_geral = 0.0

    for regiao in sorted(quantidades_por_regiao):
        total_vendas = float(round(totais_por_regiao[regiao], 2))
        if total_vendas == 0.0:
            total_vendas = 0.0

        produto_mais_vendido = min(
            produtos_por_regiao[regiao].items(),
            key=lambda item: (-item[1], item[0]),
        )[0]

        regioes[regiao] = {
            "quantidade_total": int(quantidades_por_regiao[regiao]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }
        soma_total_geral += total_vendas

    total_geral = float(round(soma_total_geral, 2))
    if total_geral == 0.0:
        total_geral = 0.0

    resumo = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as arquivo_saida:
        json.dump(resumo, arquivo_saida, ensure_ascii=False, indent=2)

    return resumo
