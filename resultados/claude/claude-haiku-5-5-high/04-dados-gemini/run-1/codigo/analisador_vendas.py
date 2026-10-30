import csv
import json
import math
import os


def processar_vendas(
    caminho_csv: str,
    caminho_json_saida: str,
    status_filtro: str = "concluido",
    top_n: int = 3,
) -> dict:
    if not os.path.isfile(caminho_csv):
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}")
    if type(top_n) is not int:
        raise TypeError("top_n deve ser um inteiro")
    if top_n < 1:
        raise ValueError("top_n deve ser maior ou igual a 1")

    status_alvo = status_filtro.strip().lower()
    total_transacoes = 0
    receita_bruta = 0.0
    receita_por_categoria = {}
    receita_por_cliente = {}

    # utf-8-sig remove o BOM inicial; arquivo com 0 bytes não produz linhas
    with open(caminho_csv, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames is not None:
            leitor.fieldnames = [
                campo.replace("﻿", "").strip() for campo in leitor.fieldnames
            ]

        for linha in leitor:
            status = (linha.get("status") or "").strip().lower()
            if status != status_alvo:
                continue

            cliente = (linha.get("cliente") or "").strip()
            categoria = (linha.get("categoria") or "").strip()
            if not cliente or not categoria:
                continue

            try:
                valor = float(linha.get("valor") or "")
            except ValueError:
                continue
            if not math.isfinite(valor) or valor < 0:
                continue

            total_transacoes += 1
            receita_bruta += valor
            receita_por_categoria[categoria] = (
                receita_por_categoria.get(categoria, 0.0) + valor
            )
            receita_por_cliente[cliente] = receita_por_cliente.get(cliente, 0.0) + valor

    receita_total = round(receita_bruta, 2)
    ticket_medio = (
        round(receita_total / total_transacoes, 2) if total_transacoes else 0.0
    )

    por_categoria = {
        categoria: round(receita_por_categoria[categoria], 2)
        for categoria in sorted(receita_por_categoria)
    }

    totais_clientes = {
        cliente: round(total, 2) for cliente, total in receita_por_cliente.items()
    }
    ranking = sorted(totais_clientes.items(), key=lambda item: (-item[1], item[0]))
    top_clientes = [
        {"cliente": cliente, "total": total} for cliente, total in ranking[:top_n]
    ]

    resultado = {
        "total_transacoes": total_transacoes,
        "receita_total": receita_total,
        "ticket_medio": ticket_medio,
        "por_categoria": por_categoria,
        "top_clientes": top_clientes,
    }

    caminho_saida = os.path.abspath(caminho_json_saida)
    os.makedirs(os.path.dirname(caminho_saida), exist_ok=True)
    with open(caminho_saida, "w", encoding="utf-8") as saida:
        json.dump(resultado, saida, indent=2, ensure_ascii=False)

    return resultado
