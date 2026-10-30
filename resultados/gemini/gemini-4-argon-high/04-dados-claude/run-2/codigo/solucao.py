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

    with caminho_entrada.open(mode="r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.reader(f)
        try:
            cabecalho_bruto = next(leitor)
        except StopIteration as exc:
            raise ValueError("Arquivo CSV vazio (sem cabeçalho).") from exc

        cabecalho = [col.strip() for col in cabecalho_bruto]
        if not COLUNAS_OBRIGATORIAS.issubset(cabecalho):
            raise ValueError("Colunas obrigatórias ausentes no cabeçalho.")

        num_colunas = len(cabecalho)
        idx_regiao = cabecalho.index("regiao")
        idx_produto = cabecalho.index("produto")
        idx_quantidade = cabecalho.index("quantidade")
        idx_preco = cabecalho.index("preco_unitario")
        idx_status = cabecalho.index("status")

        linhas_invalidas = 0
        agregado_regioes: dict[str, dict] = {}

        for linha in leitor:
            if not linha or all(campo.strip() == "" for campo in linha):
                continue

            if len(linha) != num_colunas:
                linhas_invalidas += 1
                continue

            campos = [campo.strip() for campo in linha]
            regiao = campos[idx_regiao]
            produto = campos[idx_produto]
            qtd_str = campos[idx_quantidade]
            preco_str = campos[idx_preco]
            status = campos[idx_status]

            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(qtd_str)
                preco_unitario = float(preco_str)
            except ValueError:
                linhas_invalidas += 1
                continue

            if (
                quantidade <= 0
                or not math.isfinite(preco_unitario)
                or preco_unitario < 0
            ):
                linhas_invalidas += 1
                continue

            if status.lower() != "concluida":
                continue

            if regiao not in agregado_regioes:
                agregado_regioes[regiao] = {
                    "quantidade_total": 0,
                    "total_vendas": 0.0,
                    "produtos": {},
                }

            dados_regiao = agregado_regioes[regiao]
            dados_regiao["quantidade_total"] += quantidade
            dados_regiao["total_vendas"] += quantidade * preco_unitario
            produtos_regiao = dados_regiao["produtos"]
            produtos_regiao[produto] = produtos_regiao.get(produto, 0) + quantidade

    regioes_resultado: dict[str, dict] = {}
    for regiao in sorted(agregado_regioes.keys()):
        dados = agregado_regioes[regiao]
        produtos = dados["produtos"]
        produto_mais_vendido = min(
            produtos.items(), key=lambda item: (-item[1], item[0])
        )[0]
        total_vendas_regiao = float(round(dados["total_vendas"], 2))
        if total_vendas_regiao == 0.0:
            total_vendas_regiao = 0.0

        regioes_resultado[regiao] = {
            "quantidade_total": int(dados["quantidade_total"]),
            "total_vendas": total_vendas_regiao,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(
        round(sum(r["total_vendas"] for r in regioes_resultado.values()), 2)
    )
    if total_geral == 0.0:
        total_geral = 0.0

    resultado = {
        "regioes": regioes_resultado,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open(mode="w", encoding="utf-8") as f_out:
        json.dump(resultado, f_out, ensure_ascii=False, indent=2)

    return resultado
