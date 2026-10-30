import csv
import json
import math
from collections import defaultdict
from pathlib import Path

COLUNAS = ("data", "regiao", "produto", "quantidade", "preco_unitario", "status")


def _linha_vazia(row: list[str]) -> bool:
    if not row:
        return True
    return len(row) == 1 and row[0].strip() == ""


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    caminho_entrada = Path(entrada)
    caminho_saida = Path(saida)

    with caminho_entrada.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = None
        for linha in leitor:
            if _linha_vazia(linha):
                continue
            cabecalho = linha
            break
        if cabecalho is None:
            raise ValueError("CSV sem cabeçalho")

        nomes = [coluna.strip() for coluna in cabecalho]
        indices: dict[str, int] = {}
        for indice, nome in enumerate(nomes):
            if nome not in indices:
                indices[nome] = indice
        ausentes = [coluna for coluna in COLUNAS if coluna not in indices]
        if ausentes:
            raise ValueError(
                "Colunas obrigatórias ausentes: " + ", ".join(ausentes)
            )

        n_colunas = len(cabecalho)
        i_regiao = indices["regiao"]
        i_produto = indices["produto"]
        i_quantidade = indices["quantidade"]
        i_preco = indices["preco_unitario"]
        i_status = indices["status"]

        qtd_produto: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
        total_bruto: dict[str, float] = defaultdict(float)
        linhas_invalidas = 0

        for linha in leitor:
            if _linha_vazia(linha):
                continue
            if len(linha) != n_colunas:
                linhas_invalidas += 1
                continue

            valores = [campo.strip() for campo in linha]
            regiao = valores[i_regiao]
            produto = valores[i_produto]
            if regiao == "" or produto == "":
                linhas_invalidas += 1
                continue

            try:
                quantidade = int(valores[i_quantidade])
            except (TypeError, ValueError):
                linhas_invalidas += 1
                continue
            if quantidade <= 0:
                linhas_invalidas += 1
                continue

            try:
                preco = float(valores[i_preco])
            except (TypeError, ValueError):
                linhas_invalidas += 1
                continue
            if not math.isfinite(preco) or preco < 0:
                linhas_invalidas += 1
                continue

            if valores[i_status].lower() != "concluida":
                continue

            qtd_produto[regiao][produto] += quantidade
            total_bruto[regiao] += quantidade * preco

    regioes: dict[str, dict] = {}
    for regiao in sorted(qtd_produto):
        por_produto = qtd_produto[regiao]
        mais_vendido = min(
            por_produto,
            key=lambda nome: (-por_produto[nome], nome),
        )
        regioes[regiao] = {
            "quantidade_total": int(sum(por_produto.values())),
            "total_vendas": float(round(total_bruto[regiao], 2)),
            "produto_mais_vendido": mais_vendido,
        }

    resultado = {
        "regioes": regioes,
        "total_geral": float(round(sum(item["total_vendas"] for item in regioes.values()), 2)),
        "linhas_invalidas": int(linhas_invalidas),
    }

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    caminho_saida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return resultado
