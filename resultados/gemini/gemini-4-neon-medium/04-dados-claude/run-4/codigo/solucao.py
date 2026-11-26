from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path

COLUNAS_OBRIGATORIAS = frozenset(
    {"data", "regiao", "produto", "quantidade", "preco_unitario", "status"}
)


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        cabecalho_bruto = next(reader, None)
        if cabecalho_bruto is None:
            raise ValueError("Arquivo CSV vazio: faltam colunas obrigatórias.")

        cabecalho = [col.strip() for col in cabecalho_bruto]
        num_colunas = len(cabecalho)
        indices = {nome: idx for idx, nome in enumerate(cabecalho)}

        faltantes = COLUNAS_OBRIGATORIAS - indices.keys()
        if faltantes:
            raise ValueError(
                f"Colunas obrigatórias ausentes: {', '.join(sorted(faltantes))}"
            )

        idx_regiao = indices["regiao"]
        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_unitario"]
        idx_status = indices["status"]

        linhas_invalidas = 0
        qtd_por_regiao: dict[str, int] = defaultdict(int)
        vendas_por_regiao: dict[str, float] = defaultdict(float)
        produtos_por_regiao: dict[str, dict[str, int]] = defaultdict(
            lambda: defaultdict(int)
        )

        for linha in reader:
            if not linha or (len(linha) == 1 and not linha[0].strip()):
                continue

            if len(linha) != num_colunas:
                linhas_invalidas += 1
                continue

            regiao = linha[idx_regiao].strip()
            produto = linha[idx_produto].strip()
            quantidade_str = linha[idx_quantidade].strip()
            preco_str = linha[idx_preco].strip()
            status = linha[idx_status].strip()

            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(quantidade_str)
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

            qtd_por_regiao[regiao] += quantidade
            vendas_por_regiao[regiao] += quantidade * preco_unitario
            produtos_por_regiao[regiao][produto] += quantidade

    regioes: dict[str, dict[str, int | float | str]] = {}
    for regiao in sorted(qtd_por_regiao):
        produtos = produtos_por_regiao[regiao]
        produto_mais_vendido = min(
            produtos.items(), key=lambda item: (-item[1], item[0])
        )[0]
        total_vendas = float(round(vendas_por_regiao[regiao], 2)) + 0.0
        regioes[regiao] = {
            "quantidade_total": int(qtd_por_regiao[regiao]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = (
        float(round(sum(dados["total_vendas"] for dados in regioes.values()), 2)) + 0.0
    )

    resultado = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado
