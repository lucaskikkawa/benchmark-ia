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


def _processar_linha(
    row: list[str],
    num_colunas: int,
    indices: dict[str, int],
) -> tuple[str, str, int, float, str] | None:
    """Valida e extrai os campos relevantes de uma linha não vazia.

    Retorna None se a linha for inválida.
    """
    if len(row) != num_colunas:
        return None

    valores = [campo.strip() for campo in row]
    regiao = valores[indices["regiao"]]
    produto = valores[indices["produto"]]
    if not regiao or not produto:
        return None

    try:
        quantidade = int(valores[indices["quantidade"]])
        preco_unitario = float(valores[indices["preco_unitario"]])
    except ValueError:
        return None

    if quantidade <= 0 or not math.isfinite(preco_unitario) or preco_unitario < 0:
        return None

    status = valores[indices["status"]]
    return regiao, produto, quantidade, preco_unitario, status


def resumir_vendas(entrada: str | Path, saida: str | Path) -> dict:
    """Lê um CSV de vendas, agrega os dados por região e escreve o resumo em JSON."""
    entrada_path = Path(entrada)
    saida_path = Path(saida)

    regioes_qtd: dict[str, int] = defaultdict(int)
    regioes_total: dict[str, float] = defaultdict(float)
    regioes_produtos: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    linhas_invalidas = 0

    with entrada_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)
        cabecalho = next(reader, None)
        if cabecalho is None:
            raise ValueError("Arquivo CSV vazio ou sem cabeçalho.")

        cabecalho_limpo = [col.strip() for col in cabecalho]
        indices = {nome: idx for idx, nome in enumerate(cabecalho_limpo)}
        faltantes = [col for col in COLUNAS_OBRIGATORIAS if col not in indices]
        if faltantes:
            raise ValueError(f"Colunas obrigatórias ausentes: {', '.join(faltantes)}")

        num_colunas = len(cabecalho)
        for row in reader:
            if not row:
                continue

            processada = _processar_linha(row, num_colunas, indices)
            if processada is None:
                linhas_invalidas += 1
                continue

            regiao, produto, quantidade, preco_unitario, status = processada
            if status.lower() != "concluida":
                continue

            regioes_qtd[regiao] += quantidade
            regioes_total[regiao] += quantidade * preco_unitario
            regioes_produtos[regiao][produto] += quantidade

    regioes_resumo: dict[str, dict] = {}
    for regiao in sorted(regioes_qtd):
        produto_mais_vendido = min(
            regioes_produtos[regiao].items(),
            key=lambda item: (-item[1], item[0]),
        )[0]
        regioes_resumo[regiao] = {
            "quantidade_total": int(regioes_qtd[regiao]),
            "total_vendas": float(round(regioes_total[regiao], 2)),
            "produto_mais_vendido": produto_mais_vendido,
        }

    total_geral = float(
        round(sum(info["total_vendas"] for info in regioes_resumo.values()), 2)
    )

    resultado = {
        "regioes": regioes_resumo,
        "total_geral": total_geral,
        "linhas_invalidas": int(linhas_invalidas),
    }

    saida_path.parent.mkdir(parents=True, exist_ok=True)
    with saida_path.open("w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False, indent=2)

    return resultado
