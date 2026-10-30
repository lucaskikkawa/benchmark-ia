"""Agregação de vendas a partir de um CSV de transações."""

from __future__ import annotations

import csv
import json
import math
import os
from collections import defaultdict


def processar_vendas(
    caminho_csv: str,
    caminho_json_saida: str,
    status_filtro: str = "concluido",
    top_n: int = 3,
) -> dict:
    """Lê transações em CSV, agrega as vendas filtradas e grava o resultado em JSON.

    Considera apenas linhas cujo status coincide com ``status_filtro``
    (sem distinção de maiúsculas e sem espaços nas pontas) e cujo valor é um
    número finito não negativo. O dicionário retornado é o mesmo gravado em
    ``caminho_json_saida``.
    """
    if not _arquivo_regular(caminho_csv):
        raise FileNotFoundError(caminho_csv)

    if type(top_n) is not int:
        raise TypeError("top_n deve ser um int")

    if top_n < 1:
        raise ValueError("top_n deve ser maior ou igual a 1")

    if os.path.getsize(caminho_csv) == 0:
        resultado = _metricas_vazias()
    else:
        resultado = _calcular_metricas(caminho_csv, status_filtro, top_n)

    _salvar_json(caminho_json_saida, resultado)
    return resultado


def _arquivo_regular(caminho) -> bool:
    try:
        return os.path.isfile(caminho)
    except (TypeError, ValueError, OSError):
        return False


def _metricas_vazias() -> dict:
    return {
        "total_transacoes": 0,
        "receita_total": 0.0,
        "ticket_medio": 0.0,
        "por_categoria": {},
        "top_clientes": [],
    }


def _arredondar(valor: float) -> float:
    return float(round(valor, 2))


def _texto(valor) -> str:
    if valor is None or isinstance(valor, list):
        return ""
    return str(valor).strip()


def _calcular_metricas(caminho_csv: str, status_filtro: str, top_n: int) -> dict:
    filtro = _texto(status_filtro).casefold()
    valores_categoria: dict[str, list[float]] = defaultdict(list)
    valores_cliente: dict[str, list[float]] = defaultdict(list)
    valores: list[float] = []

    with open(caminho_csv, encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames:
            leitor.fieldnames = [
                (nome or "").replace("\ufeff", "").strip() for nome in leitor.fieldnames
            ]

        for linha in leitor:
            if not linha:
                continue
            if not any(_texto(campo) for campo in linha.values()):
                continue

            status = _texto(linha.get("status")).casefold()
            if status != filtro:
                continue

            bruto = linha.get("valor")
            if bruto is None or isinstance(bruto, list):
                continue
            try:
                valor = float(str(bruto).strip())
            except (TypeError, ValueError):
                continue
            if valor < 0 or not math.isfinite(valor):
                continue

            cliente = _texto(linha.get("cliente"))
            categoria = _texto(linha.get("categoria"))
            valores.append(valor)
            valores_categoria[categoria].append(valor)
            valores_cliente[cliente].append(valor)

    total_transacoes = len(valores)
    if total_transacoes == 0:
        return _metricas_vazias()

    receita_total = _arredondar(sum(valores))
    ticket_medio = _arredondar(receita_total / total_transacoes)
    por_categoria = {
        categoria: _arredondar(sum(totais))
        for categoria, totais in sorted(valores_categoria.items())
    }
    top_clientes = sorted(
        (
            {"cliente": cliente, "total": _arredondar(sum(totais))}
            for cliente, totais in valores_cliente.items()
        ),
        key=lambda item: (-item["total"], item["cliente"]),
    )[:top_n]

    return {
        "total_transacoes": total_transacoes,
        "receita_total": receita_total,
        "ticket_medio": ticket_medio,
        "por_categoria": por_categoria,
        "top_clientes": top_clientes,
    }


def _salvar_json(caminho_json_saida: str, resultado: dict) -> None:
    pasta = os.path.dirname(os.path.abspath(caminho_json_saida))
    os.makedirs(pasta, exist_ok=True)
    texto = json.dumps(resultado, indent=2, ensure_ascii=False)
    with open(caminho_json_saida, "w", encoding="utf-8") as arquivo:
        arquivo.write(texto)
