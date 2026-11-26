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


def _processar_linha(
    row: list[str],
    indices: dict[str, int],
    num_colunas: int,
) -> tuple[str, str, int, float, str] | None:
    """Valida e extrai os campos relevantes de uma linha, ou retorna None se inválida."""
    if len(row) != num_colunas:
        return None

    limpos = [campo.strip() for campo in row]
    regiao = limpos[indices["regiao"]]
    produto = limpos[indices["produto"]]
    if not regiao or not produto:
        return None

    try:
        quantidade = int(limpos[indices["quantidade"]])
        preco_unitario = float(limpos[indices["preco_unitario"]])
    except ValueError:
        return None

    if quantidade <= 0 or not math.isfinite(preco_unitario) or preco_unitario < 0:
        return None

    status = limpos[indices["status"]]
    return regiao, produto, quantidade, preco_unitario, status


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Lê um CSV de vendas, agrega os dados concluídos por região e grava o resumo em JSON."""
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    linhas_invalidas = 0
    agregados: dict[str, dict] = {}

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        colunas = [col.strip() for col in cabecalho]
        indices = {nome: idx for idx, nome in enumerate(colunas)}
        faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in indices]
        if faltantes:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

        num_colunas = len(colunas)

        for row in leitor:
            if not row:
                continue

            extraido = _processar_linha(row, indices, num_colunas)
            if extraido is None:
                linhas_invalidas += 1
                continue

            regiao, produto, quantidade, preco_unitario, status = extraido
            if status.lower() != "concluida":
                continue

            dados_regiao = agregados.get(regiao)
            if dados_regiao is None:
                dados_regiao = {
                    "quantidade_total": 0,
                    "total_vendas": 0.0,
                    "produtos": defaultdict(int),
                }
                agregados[regiao] = dados_regiao

            dados_regiao["quantidade_total"] += quantidade
            dados_regiao["total_vendas"] += quantidade * preco_unitario
            dados_regiao["produtos"][produto] += quantidade

    regioes: dict[str, dict] = {}
    for regiao in sorted(agregados):
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

    total_geral = float(round(sum(info["total_vendas"] for info in regioes.values()), 2))
    if total_geral == 0.0:
        total_geral = 0.0

    resultado = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as arquivo_saida:
        json.dump(resultado, arquivo_saida, ensure_ascii=False, indent=2)

    return resultado
