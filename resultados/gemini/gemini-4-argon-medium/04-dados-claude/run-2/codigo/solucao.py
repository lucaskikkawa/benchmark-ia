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
        indices = {nome: cabecalho.index(nome) for nome in COLUNAS_OBRIGATORIAS}
        idx_regiao = indices["regiao"]
        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_unitario"]
        idx_status = indices["status"]

        linhas_invalidas = 0
        agregado: dict[str, dict] = {}

        for linha in leitor:
            if not linha or (len(linha) == 1 and linha[0].strip() == ""):
                continue

            if len(linha) != num_colunas:
                linhas_invalidas += 1
                continue

            campos = [valor.strip() for valor in linha]

            regiao = campos[idx_regiao]
            produto = campos[idx_produto]
            if not regiao or not produto:
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(campos[idx_quantidade])
            except ValueError:
                linhas_invalidas += 1
                continue
            if quantidade <= 0:
                linhas_invalidas += 1
                continue

            try:
                preco_unitario = float(campos[idx_preco])
            except ValueError:
                linhas_invalidas += 1
                continue
            if not math.isfinite(preco_unitario) or preco_unitario < 0:
                linhas_invalidas += 1
                continue

            status = campos[idx_status]
            if status.casefold() != "concluida" or status.lower() != "concluida":
                continue

            dados_regiao = agregado.setdefault(
                regiao,
                {
                    "quantidade_total": 0,
                    "total_vendas": 0.0,
                    "produtos": {},
                },
            )
            dados_regiao["quantidade_total"] += quantidade
            dados_regiao["total_vendas"] += quantidade * preco_unitario
            produtos_regiao = dados_regiao["produtos"]
            produtos_regiao[produto] = produtos_regiao.get(produto, 0) + quantidade

    regioes_ordenadas = {}
    for regiao in sorted(agregado.keys()):
        dados = agregado[regiao]
        produtos = dados["produtos"]
        produto_mais_vendido = min(
            produtos.items(), key=lambda item: (-item[1], item[0])
        )[0]
        total_vendas_regiao = round(float(dados["total_vendas"]), 2) + 0.0
        regioes_ordenadas[regiao] = {
            "quantidade_total": int(dados["quantidade_total"]),
            "total_vendas": total_vendas_regiao,
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = (
        round(
            float(sum(r["total_vendas"] for r in regioes_ordenadas.values())),
            2,
        )
        + 0.0
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
