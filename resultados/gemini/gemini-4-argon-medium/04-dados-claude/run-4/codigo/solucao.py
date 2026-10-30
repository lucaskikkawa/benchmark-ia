import csv
import json
import math
from pathlib import Path

COLUNAS_OBRIGATORIAS = {
    "data",
    "regiao",
    "produto",
    "quantidade",
    "preco_unitario",
    "status",
}


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    caminho_entrada = Path(entrada)
    caminho_saida = Path(saida)

    with caminho_entrada.open("r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.reader(f, delimiter=",", quotechar='"')
        try:
            cabecalho_bruto = next(leitor)
        except StopIteration:
            raise ValueError("Arquivo CSV vazio (sem cabeçalho).")

        cabecalho = [col.strip() for col in cabecalho_bruto]
        if not COLUNAS_OBRIGATORIAS.issubset(set(cabecalho)):
            raise ValueError("Faltam colunas obrigatórias no cabeçalho.")

        indices = {col: idx for idx, col in enumerate(cabecalho)}
        num_colunas = len(cabecalho)

        idx_regiao = indices["regiao"]
        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_unitario"]
        idx_status = indices["status"]

        linhas_invalidas = 0
        dados_regioes: dict[str, dict] = {}

        for linha in leitor:
            if not linha or all(campo.strip() == "" for campo in linha):
                continue

            if len(linha) != num_colunas:
                linhas_invalidas += 1
                continue

            regiao = linha[idx_regiao].strip()
            produto = linha[idx_produto].strip()
            qtd_str = linha[idx_quantidade].strip()
            preco_str = linha[idx_preco].strip()
            status = linha[idx_status].strip()

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
                preco = float(preco_str)
            except ValueError:
                linhas_invalidas += 1
                continue

            if not math.isfinite(preco) or preco < 0:
                linhas_invalidas += 1
                continue

            if status.lower() != "concluida":
                continue

            if regiao not in dados_regioes:
                dados_regioes[regiao] = {
                    "quantidade_total": 0,
                    "total_vendas": 0.0,
                    "produtos": {},
                }

            info = dados_regioes[regiao]
            info["quantidade_total"] += quantidade
            info["total_vendas"] += quantidade * preco
            info["produtos"][produto] = info["produtos"].get(produto, 0) + quantidade

    regioes_resumo: dict[str, dict] = {}
    for regiao in sorted(dados_regioes.keys()):
        info = dados_regioes[regiao]
        produtos = info["produtos"]
        produto_mais_vendido = min(
            produtos.keys(), key=lambda p: (-produtos[p], p)
        )
        total_vendas_regiao = float(round(info["total_vendas"], 2))
        if total_vendas_regiao == 0.0:
            total_vendas_regiao = 0.0

        regioes_resumo[regiao] = {
            "quantidade_total": int(info["quantidade_total"]),
            "total_vendas": total_vendas_regiao,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(
        round(sum(r["total_vendas"] for r in regioes_resumo.values()), 2)
    )
    if total_geral == 0.0:
        total_geral = 0.0

    resultado = {
        "regioes": regioes_resumo,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open("w", encoding="utf-8") as f_out:
        json.dump(resultado, f_out, ensure_ascii=False, indent=2)

    return resultado
