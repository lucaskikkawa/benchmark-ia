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
            raise ValueError("Arquivo CSV vazio, sem cabeçalho.")

        cabecalho = [col.strip() for col in cabecalho_bruto]
        if not COLUNAS_OBRIGATORIAS.issubset(cabecalho):
            raise ValueError("Faltam colunas obrigatórias no cabeçalho.")

        num_colunas = len(cabecalho)
        idx = {nome: i for i, nome in enumerate(cabecalho)}

        idx_regiao = idx["regiao"]
        idx_produto = idx["produto"]
        idx_quantidade = idx["quantidade"]
        idx_preco = idx["preco_unitario"]
        idx_status = idx["status"]

        linhas_invalidas = 0
        agregado: dict[str, dict] = {}

        for linha_bruta in leitor:
            if not linha_bruta or (len(linha_bruta) == 1 and linha_bruta[0].strip() == ""):
                continue

            if len(linha_bruta) != num_colunas:
                linhas_invalidas += 1
                continue

            regiao = linha_bruta[idx_regiao].strip()
            produto = linha_bruta[idx_produto].strip()
            quantidade_str = linha_bruta[idx_quantidade].strip()
            preco_str = linha_bruta[idx_preco].strip()
            status = linha_bruta[idx_status].strip()

            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(quantidade_str)
                preco_unitario = float(preco_str)
            except ValueError:
                linhas_invalidas += 1
                continue

            if quantidade <= 0 or not math.isfinite(preco_unitario) or preco_unitario < 0:
                linhas_invalidas += 1
                continue

            if status.lower() != "concluida":
                continue

            if regiao not in agregado:
                agregado[regiao] = {
                    "quantidade_total": 0,
                    "total_vendas": 0.0,
                    "produtos": {},
                }

            dados_regiao = agregado[regiao]
            dados_regiao["quantidade_total"] += quantidade
            dados_regiao["total_vendas"] += quantidade * preco_unitario
            produtos_regiao = dados_regiao["produtos"]
            produtos_regiao[produto] = produtos_regiao.get(produto, 0) + quantidade

    regioes_ordenadas: dict[str, dict] = {}
    for regiao in sorted(agregado.keys()):
        dados = agregado[regiao]
        produtos = dados["produtos"]
        produto_mais_vendido = min(
            produtos.items(), key=lambda item: (-item[1], item[0])
        )[0]
        regioes_ordenadas[regiao] = {
            "quantidade_total": int(dados["quantidade_total"]),
            "total_vendas": float(round(dados["total_vendas"], 2)),
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(
        round(sum(r["total_vendas"] for r in regioes_ordenadas.values()), 2)
    )

    resultado = {
        "regioes": regioes_ordenadas,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open("w", encoding="utf-8") as f_out:
        json.dump(resultado, f_out, ensure_ascii=False, indent=2)

    return resultado
