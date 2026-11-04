"""Processamento de dados financeiros: lê vendas de um CSV e gera métricas em JSON."""

import csv
import json
import math
import os


def _converter_valor(bruto):
    """Converte o valor para float; retorna None se inválido, negativo ou não finito."""
    if bruto is None:
        return None
    try:
        valor = float(str(bruto).strip())
    except (TypeError, ValueError):
        return None
    if not math.isfinite(valor) or valor < 0:
        return None
    return valor


def _ler_linhas(caminho_csv):
    """Lê o CSV retornando dicionários com cabeçalhos normalizados."""
    with open(caminho_csv, "r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.reader(arquivo)
        cabecalho = None
        for linha in leitor:
            if cabecalho is None:
                if not linha or all(not campo.strip() for campo in linha):
                    continue
                cabecalho = [campo.lstrip("﻿").strip() for campo in linha]
                continue
            if not linha or all(not campo.strip() for campo in linha):
                continue
            yield dict(zip(cabecalho, linha))


def processar_vendas(
    caminho_csv: str,
    caminho_json_saida: str,
    status_filtro: str = "concluido",
    top_n: int = 3,
) -> dict:
    if not os.path.isfile(caminho_csv):
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}")
    if type(top_n) is not int:
        raise TypeError("top_n deve ser um número inteiro")
    if top_n < 1:
        raise ValueError("top_n deve ser maior ou igual a 1")

    filtro = str(status_filtro).strip().lower()

    total_transacoes = 0
    receita = 0.0
    por_categoria = {}
    por_cliente = {}

    if os.path.getsize(caminho_csv) > 0:
        for linha in _ler_linhas(caminho_csv):
            status = linha.get("status")
            if status is None or status.strip().lower() != filtro:
                continue
            valor = _converter_valor(linha.get("valor"))
            if valor is None:
                continue
            cliente = linha.get("cliente")
            categoria = linha.get("categoria")
            if cliente is None or categoria is None:
                continue
            cliente = cliente.strip()
            categoria = categoria.strip()

            total_transacoes += 1
            receita += valor
            por_categoria[categoria] = por_categoria.get(categoria, 0.0) + valor
            por_cliente[cliente] = por_cliente.get(cliente, 0.0) + valor

    receita_total = round(receita, 2)
    ticket_medio = round(receita_total / total_transacoes, 2) if total_transacoes else 0.0

    categorias_ordenadas = {
        categoria: round(por_categoria[categoria], 2)
        for categoria in sorted(por_categoria)
    }

    clientes = [(nome, round(total, 2)) for nome, total in por_cliente.items()]
    clientes.sort(key=lambda item: (-item[1], item[0]))
    top_clientes = [
        {"cliente": nome, "total": total} for nome, total in clientes[:top_n]
    ]

    resultado = {
        "total_transacoes": total_transacoes,
        "receita_total": float(receita_total),
        "ticket_medio": float(ticket_medio),
        "por_categoria": categorias_ordenadas,
        "top_clientes": top_clientes,
    }

    diretorio = os.path.dirname(os.path.abspath(os.fspath(caminho_json_saida)))
    if diretorio:
        os.makedirs(diretorio, exist_ok=True)
    with open(caminho_json_saida, "w", encoding="utf-8") as saida:
        json.dump(resultado, saida, indent=2, ensure_ascii=False)

    return resultado
