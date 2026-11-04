"""Leitura de vendas em CSV e geração de um resumo financeiro em JSON."""

import csv
import json
import math
from collections import defaultdict
from pathlib import Path


def processar_vendas(
    caminho_csv: str,
    caminho_json_saida: str,
    status_filtro: str = "concluido",
    top_n: int = 3,
) -> dict:
    """Agregue vendas válidas pelo status e salve e retorne suas métricas."""
    entrada = Path(caminho_csv)
    if not entrada.is_file():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}")
    if type(top_n) is not int:
        raise TypeError("top_n deve ser um número inteiro")
    if top_n < 1:
        raise ValueError("top_n deve ser maior ou igual a 1")

    filtro = status_filtro.strip().casefold()
    total_transacoes = 0
    receita = 0.0
    categorias = defaultdict(float)
    clientes = defaultdict(float)

    with entrada.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo, skipinitialspace=True)
        # Também permita linhas em branco antes do cabeçalho.
        cabecalho = next(
            (linha for linha in leitor if any(campo.strip() for campo in linha)),
            [],
        )
        colunas = [campo.strip().lstrip("\ufeff").strip() for campo in cabecalho]

        for linha in leitor:
            if not any(campo.strip() for campo in linha):
                continue
            registro = dict(zip(colunas, linha))
            if registro.get("status", "").strip().casefold() != filtro:
                continue
            try:
                valor = float(registro.get("valor", ""))
            except (TypeError, ValueError):
                continue
            # NaN e infinito não representam valores financeiros válidos.
            if not math.isfinite(valor) or valor < 0:
                continue

            cliente = registro.get("cliente", "").strip()
            categoria = registro.get("categoria", "").strip()
            total_transacoes += 1
            receita += valor
            categorias[categoria] += valor
            clientes[cliente] += valor

    receita_total = round(receita, 2)
    ranking = [
        {"cliente": cliente, "total": round(total, 2)}
        for cliente, total in clientes.items()
    ]
    ranking.sort(key=lambda item: (-item["total"], item["cliente"]))
    resultado = {
        "total_transacoes": total_transacoes,
        "receita_total": receita_total,
        "ticket_medio": (
            round(receita_total / total_transacoes, 2) if total_transacoes else 0.0
        ),
        "por_categoria": {
            categoria: round(categorias[categoria], 2)
            for categoria in sorted(categorias)
        },
        "top_clientes": ranking[:top_n],
    }

    saida = Path(caminho_json_saida)
    saida.parent.mkdir(parents=True, exist_ok=True)
    with saida.open("w", encoding="utf-8") as arquivo:
        json.dump(resultado, arquivo, indent=2, ensure_ascii=False)

    return resultado
