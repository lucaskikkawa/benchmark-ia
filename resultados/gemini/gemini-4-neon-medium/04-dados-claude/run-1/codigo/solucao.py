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


def _arredondar_moeda(valor: float) -> float:
    resultado = float(round(valor, 2))
    return 0.0 if resultado == 0.0 else resultado


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    with entrada_path.open(mode="r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho_bruto = next(leitor, None)
        if cabecalho_bruto is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        cabecalho = [coluna.strip() for coluna in cabecalho_bruto]
        indices: dict[str, int] = {}
        for idx, nome in enumerate(cabecalho):
            if nome not in indices:
                indices[nome] = idx

        faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in indices]
        if faltantes:
            raise ValueError(
                f"Colunas obrigatórias ausentes no cabeçalho: {', '.join(faltantes)}"
            )

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
            if not linha or (len(linha) == 1 and not linha[0].strip()):
                continue

            valores = [campo.strip() for campo in linha]
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

            status = valores[idx_status]
            if status.lower() != "concluida":
                continue

            quantidades_por_regiao[regiao] += quantidade
            totais_por_regiao[regiao] += quantidade * preco_unitario
            produtos_por_regiao[regiao][produto] += quantidade

    regioes: dict[str, dict[str, int | float | str]] = {}
    for regiao in sorted(quantidades_por_regiao):
        produtos = produtos_por_regiao[regiao]
        produto_mais_vendido = min(
            produtos.items(), key=lambda item: (-item[1], item[0])
        )[0]
        regioes[regiao] = {
            "quantidade_total": int(quantidades_por_regiao[regiao]),
            "total_vendas": _arredondar_moeda(totais_por_regiao[regiao]),
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = _arredondar_moeda(
        sum(dados["total_vendas"] for dados in regioes.values())
    )

    resumo = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open(mode="w", encoding="utf-8") as arquivo_saida:
        json.dump(resumo, arquivo_saida, ensure_ascii=False, indent=2)

    return resumo
