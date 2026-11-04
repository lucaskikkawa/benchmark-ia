import csv
import json
import math
from pathlib import Path

COLUNAS_OBRIGATORIAS = (
    "data",
    "regiao",
    "produto",
    "quantidade",
    "preco_unitario",
    "status",
)


def _linha_totalmente_vazia(row: list[str]) -> bool:
    # csv devolve [] para linha em branco e ['   '] para linha só com espaços.
    return not row or (len(row) == 1 and not row[0].strip())


def _moeda(valor: float) -> float:
    arredondado = round(valor, 2)
    # -0.0 == 0; a saída pede o float 0.0.
    if arredondado == 0:
        return 0.0
    return float(arredondado)


def _indices_cabecalho(header: list[str]) -> dict[str, int]:
    indices: dict[str, int] = {}
    for i, nome in enumerate(header):
        chave = nome.strip()
        if chave and chave not in indices:
            indices[chave] = i
    faltando = [coluna for coluna in COLUNAS_OBRIGATORIAS if coluna not in indices]
    if faltando:
        raise ValueError(
            "Colunas obrigatórias ausentes: " + ", ".join(faltando)
        )
    return indices


def _agregar(reader: csv.reader, header: list[str]) -> dict:
    indices = _indices_cabecalho(header)
    n_cols = len(header)
    idx_regiao = indices["regiao"]
    idx_produto = indices["produto"]
    idx_quantidade = indices["quantidade"]
    idx_preco = indices["preco_unitario"]
    idx_status = indices["status"]

    agregados: dict[str, dict] = {}
    linhas_invalidas = 0

    for row in reader:
        if _linha_totalmente_vazia(row):
            continue
        if len(row) != n_cols:
            linhas_invalidas += 1
            continue

        regiao = row[idx_regiao].strip()
        produto = row[idx_produto].strip()
        quantidade_txt = row[idx_quantidade].strip()
        preco_txt = row[idx_preco].strip()
        status = row[idx_status].strip()

        if not regiao or not produto:
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

        bloco = agregados.get(regiao)
        if bloco is None:
            bloco = {"quantidade_total": 0, "total_raw": 0.0, "produtos": {}}
            agregados[regiao] = bloco
        bloco["quantidade_total"] += quantidade
        bloco["total_raw"] += quantidade * preco
        produtos = bloco["produtos"]
        produtos[produto] = produtos.get(produto, 0) + quantidade

    regioes: dict[str, dict] = {}
    for nome in sorted(agregados):
        bloco = agregados[nome]
        produtos = bloco["produtos"]
        produto_mais = min(produtos, key=lambda nome_produto: (-produtos[nome_produto], nome_produto))
        regioes[nome] = {
            "quantidade_total": int(bloco["quantidade_total"]),
            "total_vendas": _moeda(bloco["total_raw"]),
            "produto_mais_vendido": produto_mais,
        }

    return {
        "regioes": regioes,
        "total_geral": _moeda(sum(item["total_vendas"] for item in regioes.values())),
        "linhas_invalidas": int(linhas_invalidas),
    }


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    origem = Path(entrada)
    with origem.open(encoding="utf-8-sig", newline="") as arquivo:
        reader = csv.reader(arquivo)
        header = None
        for row in reader:
            if _linha_totalmente_vazia(row):
                continue
            header = row
            break
        if header is None:
            raise ValueError("CSV sem cabeçalho")
        resumo = _agregar(reader, header)

    destino = Path(saida)
    destino.parent.mkdir(parents=True, exist_ok=True)
    destino.write_text(
        json.dumps(resumo, ensure_ascii=False, indent=2),
        encoding="utf-8",
        newline="\n",
    )
    return resumo
