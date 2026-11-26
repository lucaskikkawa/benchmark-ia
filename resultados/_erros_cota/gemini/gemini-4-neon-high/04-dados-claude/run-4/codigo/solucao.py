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
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    linhas_invalidas = 0
    qtd_por_regiao: dict[str, int] = defaultdict(int)
    vendas_por_regiao: dict[str, float] = defaultdict(float)
    produtos_por_regiao: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        cabecalho = next(reader, None)
        if cabecalho is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho ausente.")

        nomes_colunas = [col.strip() for col in cabecalho]
        num_colunas = len(nomes_colunas)
        indices = {nome: idx for idx, nome in enumerate(nomes_colunas)}

        faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in indices]
        if faltantes:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

        idx_regiao = indices["regiao"]
        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_unitario"]
        idx_status = indices["status"]

        for linha in reader:
            if not linha or (len(linha) == 1 and not linha[0].strip()):
                continue

            if len(linha) != num_colunas:
                linhas_invalidas += 1
                continue

            valores = [valor.strip() for valor in linha]

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

            qtd_por_regiao[regiao] += quantidade
            vendas_por_regiao[regiao] += quantidade * preco_unitario
            produtos_por_regiao[regiao][produto] += quantidade

    regioes: dict[str, dict[str, int | float | str]] = {}
    for regiao in sorted(qtd_por_regiao):
        produtos_qtd = produtos_por_regiao[regiao]
        produto_mais_vendido = min(
            produtos_qtd.items(),
            key=lambda item: (-item[1], item[0]),
        )[0]
        total_vendas = float(round(vendas_por_regiao[regiao], 2)) + 0.0
        regioes[regiao] = {
            "quantidade_total": int(qtd_por_regiao[regiao]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(round(sum((r["total_vendas"] for r in regioes.values()), 0.0), 2)) + 0.0

    resumo = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resumo, f, ensure_ascii=False, indent=2)

    return resumo
