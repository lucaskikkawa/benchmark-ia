"""Resume um CSV de vendas em um JSON agregado por região."""

import csv
import json
import math
from pathlib import Path

COLUNAS = ("data", "regiao", "produto", "quantidade", "preco_unitario", "status")


def _linha_vazia(row: list[str]) -> bool:
    return len(row) == 0


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    caminho_entrada = Path(entrada)
    caminho_saida = Path(saida)

    with caminho_entrada.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = None
        for row in leitor:
            if _linha_vazia(row):
                continue
            cabecalho = [campo.strip() for campo in row]
            break
        if cabecalho is None:
            raise ValueError("CSV sem cabeçalho")

        ausentes = [coluna for coluna in COLUNAS if coluna not in cabecalho]
        if ausentes:
            raise ValueError(
                "colunas obrigatórias ausentes: " + ", ".join(ausentes)
            )
        indices = {coluna: cabecalho.index(coluna) for coluna in COLUNAS}
        n_campos = len(cabecalho)

        linhas_invalidas = 0
        agregados: dict[str, dict] = {}

        for row in leitor:
            if _linha_vazia(row):
                continue
            if len(row) != n_campos:
                linhas_invalidas += 1
                continue

            regiao = row[indices["regiao"]].strip()
            produto = row[indices["produto"]].strip()
            quantidade_txt = row[indices["quantidade"]].strip()
            preco_txt = row[indices["preco_unitario"]].strip()
            status = row[indices["status"]].strip()

            if regiao == "" or produto == "":
                linhas_invalidas += 1
                continue
            try:
                quantidade = int(quantidade_txt)
            except ValueError:
                linhas_invalidas += 1
                continue
            if quantidade <= 0:
                linhas_invalidas += 1
                continue
            try:
                preco = float(preco_txt)
            except ValueError:
                linhas_invalidas += 1
                continue
            if not math.isfinite(preco) or preco < 0:
                linhas_invalidas += 1
                continue
            if status.lower() != "concluida":
                continue

            grupo = agregados.get(regiao)
            if grupo is None:
                grupo = {"quantidade_total": 0, "total": 0.0, "produtos": {}}
                agregados[regiao] = grupo
            grupo["quantidade_total"] += quantidade
            grupo["total"] += quantidade * preco
            grupo["produtos"][produto] = grupo["produtos"].get(produto, 0) + quantidade

    regioes: dict[str, dict] = {}
    for nome in sorted(agregados):
        grupo = agregados[nome]
        produtos: dict[str, int] = grupo["produtos"]
        mais_vendido = min(
            produtos,
            key=lambda nome_produto: (-produtos[nome_produto], nome_produto),
        )
        regioes[nome] = {
            "quantidade_total": int(grupo["quantidade_total"]),
            "total_vendas": float(round(grupo["total"], 2)),
            "produto_mais_vendido": mais_vendido,
        }

    if regioes:
        total_geral = float(
            round(sum(item["total_vendas"] for item in regioes.values()), 2)
        )
    else:
        total_geral = 0.0

    resultado = {
        "regioes": regioes,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    caminho_saida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return resultado
