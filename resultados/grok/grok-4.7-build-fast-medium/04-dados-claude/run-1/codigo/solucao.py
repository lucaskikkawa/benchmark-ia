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


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    caminho_entrada = Path(entrada)
    caminho_saida = Path(saida)

    with caminho_entrada.open(encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        try:
            cabecalho_bruto = next(leitor)
        except StopIteration:
            raise ValueError("CSV sem cabeçalho") from None

        cabecalho = [campo.strip() for campo in cabecalho_bruto]
        indices: dict[str, int] = {}
        for indice, nome in enumerate(cabecalho):
            if nome not in indices:
                indices[nome] = indice

        faltando = [nome for nome in COLUNAS_OBRIGATORIAS if nome not in indices]
        if faltando:
            raise ValueError(
                "Colunas obrigatórias ausentes: " + ", ".join(faltando)
            )

        n_colunas = len(cabecalho)
        agregados: dict[str, dict] = {}
        linhas_invalidas = 0

        for linha in leitor:
            if _linha_vazia(linha):
                continue

            valores = [campo.strip() for campo in linha]
            if len(valores) != n_colunas or not _linha_valida(valores, indices):
                linhas_invalidas += 1
                continue

            status = valores[indices["status"]]
            if status.lower() != "concluida":
                continue

            regiao = valores[indices["regiao"]]
            produto = valores[indices["produto"]]
            quantidade = int(valores[indices["quantidade"]])
            preco = float(valores[indices["preco_unitario"]])

            grupo = agregados.get(regiao)
            if grupo is None:
                grupo = {"quantidade_total": 0, "bruto": 0.0, "produtos": {}}
                agregados[regiao] = grupo
            grupo["quantidade_total"] += quantidade
            grupo["bruto"] += quantidade * preco
            grupo["produtos"][produto] = grupo["produtos"].get(produto, 0) + quantidade

    regioes: dict[str, dict] = {}
    for regiao in sorted(agregados):
        grupo = agregados[regiao]
        produtos: dict[str, int] = grupo["produtos"]
        mais_vendido = min(produtos, key=lambda nome: (-produtos[nome], nome))
        regioes[regiao] = {
            "quantidade_total": int(grupo["quantidade_total"]),
            "total_vendas": float(round(grupo["bruto"], 2)),
            "produto_mais_vendido": mais_vendido,
        }

    resultado = {
        "regioes": regioes,
        "total_geral": float(
            round(sum(item["total_vendas"] for item in regioes.values()), 2)
        ),
        "linhas_invalidas": int(linhas_invalidas),
    }

    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    caminho_saida.write_text(
        json.dumps(resultado, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return resultado


def _linha_vazia(linha: list[str]) -> bool:
    if len(linha) == 0:
        return True
    return len(linha) == 1 and linha[0].strip() == ""


def _linha_valida(valores: list[str], indices: dict[str, int]) -> bool:
    regiao = valores[indices["regiao"]]
    produto = valores[indices["produto"]]
    if not regiao or not produto:
        return False
    try:
        quantidade = int(valores[indices["quantidade"]])
    except (TypeError, ValueError):
        return False
    if quantidade <= 0:
        return False
    try:
        preco = float(valores[indices["preco_unitario"]])
    except (TypeError, ValueError):
        return False
    return math.isfinite(preco) and preco >= 0
