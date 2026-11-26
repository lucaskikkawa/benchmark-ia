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


def _parse_linha_valida(
    valores: list[str], indices: dict[str, int]
) -> tuple[str, str, int, float, str] | None:
    """Valida e converte os campos relevantes de uma linha já limpa.

    Retorna ``(regiao, produto, quantidade, preco_unitario, status)`` ou ``None``
    se a linha for inválida.
    """
    regiao = valores[indices["regiao"]]
    produto = valores[indices["produto"]]
    if not regiao or not produto:
        return None

    try:
        quantidade = int(valores[indices["quantidade"]])
    except ValueError:
        return None
    if quantidade <= 0:
        return None

    try:
        preco_unitario = float(valores[indices["preco_unitario"]])
    except ValueError:
        return None
    if not math.isfinite(preco_unitario) or preco_unitario < 0:
        return None

    status = valores[indices["status"]]
    return regiao, produto, quantidade, preco_unitario, status


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Lê um CSV de vendas, agrega os resultados por região, salva em JSON e retorna o resumo."""
    caminho_entrada = Path(entrada)
    caminho_saida = Path(saida)

    linhas_invalidas = 0
    agregado: dict[str, dict[str, object]] = {}

    with caminho_entrada.open("r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.reader(f)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        nomes_colunas = [col.strip() for col in cabecalho]
        indices = {nome: idx for idx, nome in enumerate(nomes_colunas)}

        faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in indices]
        if faltantes:
            raise ValueError(
                f"Colunas obrigatórias ausentes: {', '.join(faltantes)}"
            )

        num_colunas = len(nomes_colunas)

        for linha in leitor:
            if not linha:
                continue

            if len(linha) != num_colunas:
                linhas_invalidas += 1
                continue

            valores = [v.strip() for v in linha]
            convertida = _parse_linha_valida(valores, indices)
            if convertida is None:
                linhas_invalidas += 1
                continue

            regiao, produto, quantidade, preco_unitario, status = convertida
            if status.lower() != "concluida":
                continue

            if regiao not in agregado:
                agregado[regiao] = {
                    "quantidade_total": 0,
                    "total_vendas": 0.0,
                    "produtos": defaultdict(int),
                }

            dados_regiao = agregado[regiao]
            dados_regiao["quantidade_total"] = (
                int(dados_regiao["quantidade_total"]) + quantidade
            )
            dados_regiao["total_vendas"] = (
                float(dados_regiao["total_vendas"]) + quantidade * preco_unitario
            )
            produtos: defaultdict[str, int] = dados_regiao["produtos"]  # type: ignore[assignment]
            produtos[produto] += quantidade

    regioes: dict[str, dict[str, object]] = {}
    for regiao in sorted(agregado):
        dados_regiao = agregado[regiao]
        produtos = dados_regiao["produtos"]  # type: ignore[assignment]
        produto_mais_vendido = min(
            produtos.items(), key=lambda item: (-item[1], item[0])
        )[0]
        regioes[regiao] = {
            "quantidade_total": int(dados_regiao["quantidade_total"]),
            "total_vendas": float(round(float(dados_regiao["total_vendas"]), 2)),
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(
        round(sum(float(r["total_vendas"]) for r in regioes.values()), 2)
    )

    resumo = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open("w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)

    return resumo
