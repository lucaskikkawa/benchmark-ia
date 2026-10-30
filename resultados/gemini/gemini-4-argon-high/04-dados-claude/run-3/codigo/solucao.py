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
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    with open(entrada_path, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')
        try:
            cabecalho = next(reader)
        except StopIteration:
            raise ValueError("Arquivo CSV vazio (sem cabeçalho).")

        nomes_colunas = [col.strip() for col in cabecalho]
        indices = {nome: i for i, nome in enumerate(nomes_colunas)}

        if not COLUNAS_OBRIGATORIAS.issubset(indices):
            raise ValueError("Faltam colunas obrigatórias no cabeçalho.")

        num_colunas = len(cabecalho)
        idx_regiao = indices["regiao"]
        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_unitario"]
        idx_status = indices["status"]

        linhas_invalidas = 0
        agregado: dict[str, dict] = {}

        for linha in reader:
            valores = [campo.strip() for campo in linha]
            if not any(valores):
                continue

            if len(valores) != num_colunas:
                linhas_invalidas += 1
                continue

            regiao = valores[idx_regiao]
            produto = valores[idx_produto]
            str_quantidade = valores[idx_quantidade]
            str_preco = valores[idx_preco]
            status = valores[idx_status]

            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(str_quantidade)
            except ValueError:
                linhas_invalidas += 1
                continue

            if quantidade <= 0:
                linhas_invalidas += 1
                continue

            try:
                preco_unitario = float(str_preco)
            except ValueError:
                linhas_invalidas += 1
                continue

            if not math.isfinite(preco_unitario) or preco_unitario < 0:
                linhas_invalidas += 1
                continue

            if status.lower() != "concluida":
                continue

            if regiao not in agregado:
                agregado[regiao] = {
                    "quantidade_total": 0,
                    "soma_vendas": 0.0,
                    "produtos": {},
                }

            dados_regiao = agregado[regiao]
            dados_regiao["quantidade_total"] += quantidade
            dados_regiao["soma_vendas"] += quantidade * preco_unitario
            produtos_regiao = dados_regiao["produtos"]
            produtos_regiao[produto] = produtos_regiao.get(produto, 0) + quantidade

    regioes_ordenadas: dict[str, dict] = {}
    for regiao in sorted(agregado.keys()):
        dados = agregado[regiao]
        produtos_regiao = dados["produtos"]
        produto_mais_vendido = min(
            produtos_regiao.items(), key=lambda item: (-item[1], item[0])
        )[0]
        total_vendas = float(round(dados["soma_vendas"], 2))
        if total_vendas == 0.0:
            total_vendas = 0.0
        regioes_ordenadas[regiao] = {
            "quantidade_total": int(dados["quantidade_total"]),
            "total_vendas": total_vendas,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(
        round(sum((r["total_vendas"] for r in regioes_ordenadas.values()), 0.0), 2)
    )
    if total_geral == 0.0:
        total_geral = 0.0

    resultado = {
        "regioes": regioes_ordenadas,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with open(saida_path, mode="w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado
