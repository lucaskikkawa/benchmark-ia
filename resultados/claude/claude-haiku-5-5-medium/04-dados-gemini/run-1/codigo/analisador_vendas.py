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
    """Lê vendas de um CSV, agrega as métricas e salva o resultado em JSON."""
    if not os.path.isfile(caminho_csv):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")
    if type(top_n) is not int:
        raise TypeError("top_n deve ser um inteiro")
    if top_n < 1:
        raise ValueError("top_n deve ser maior ou igual a 1")

    status_alvo = status_filtro.strip().lower()
    total_transacoes = 0
    receita_bruta = 0.0
    receita_por_categoria = {}
    total_por_cliente = {}

    with open(caminho_csv, "r", encoding="utf-8", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        # Remove BOM e espaços das pontas dos nomes das colunas.
        # Um arquivo de 0 bytes não tem cabeçalho: o leitor não produz linhas.
        if leitor.fieldnames is not None:
            leitor.fieldnames = [
                (nome or "").replace("﻿", "").strip() for nome in leitor.fieldnames
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
                valor = float((linha.get("valor") or "").strip())
            except ValueError:
                continue
            if not math.isfinite(valor) or valor < 0:
                continue

            total_transacoes += 1
            receita_bruta += valor
            receita_por_categoria[categoria] = receita_por_categoria.get(categoria, 0.0) + valor
            total_por_cliente[cliente] = total_por_cliente.get(cliente, 0.0) + valor

    receita_total = round(receita_bruta, 2)
    ticket_medio = round(receita_total / total_transacoes, 2) if total_transacoes else 0.0

    por_categoria = {
        categoria: round(total, 2)
        for categoria, total in sorted(receita_por_categoria.items())
    }

    clientes_ordenados = sorted(
        ((cliente, round(total, 2)) for cliente, total in total_por_cliente.items()),
        key=lambda item: (-item[1], item[0]),
    )
    top_clientes = [
        {"cliente": cliente, "total": total}
        for cliente, total in clientes_ordenados[:top_n]
    ]

    resultado = {
        "total_transacoes": total_transacoes,
        "receita_total": receita_total,
        "ticket_medio": ticket_medio,
        "por_categoria": por_categoria,
        "top_clientes": top_clientes,
    }

    diretorio = os.path.dirname(os.path.abspath(caminho_json_saida))
    os.makedirs(diretorio, exist_ok=True)
    with open(caminho_json_saida, "w", encoding="utf-8") as arquivo:
        json.dump(resultado, arquivo, indent=2, ensure_ascii=False)

    return resultado
