import csv
import json
import math
import os
from collections import defaultdict


def _limpar(texto):
    if texto is None:
        return ""
    return str(texto).strip()


def processar_vendas(
    caminho_csv: str,
    caminho_json_saida: str,
    status_filtro: str = "concluido",
    top_n: int = 3,
) -> dict:
    if not os.path.isfile(caminho_csv):
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho_csv}")
    if type(top_n) is not int:
        raise TypeError("top_n deve ser um inteiro")
    if top_n < 1:
        raise ValueError("top_n deve ser >= 1")

    filtro = _limpar(status_filtro).lower()

    total_transacoes = 0
    receita = 0.0
    por_categoria = defaultdict(float)
    por_cliente = defaultdict(float)

    with open(caminho_csv, "r", encoding="utf-8-sig", newline="") as f:
        leitor = csv.reader(f)
        cabecalho = next(leitor, None)
        if cabecalho is not None:
            cabecalho = [c.lstrip("﻿").strip() for c in cabecalho]
            for linha in leitor:
                if not linha or all(not c.strip() for c in linha):
                    continue
                registro = dict(zip(cabecalho, linha))
                if _limpar(registro.get("status")).lower() != filtro:
                    continue
                try:
                    valor = float(_limpar(registro.get("valor")))
                except (TypeError, ValueError):
                    continue
                if not math.isfinite(valor) or valor < 0:
                    continue
                cliente = _limpar(registro.get("cliente"))
                categoria = _limpar(registro.get("categoria"))
                total_transacoes += 1
                receita += valor
                por_categoria[categoria] += valor
                por_cliente[cliente] += valor

    receita_total = round(receita, 2)
    ticket_medio = (
        round(receita_total / total_transacoes, 2) if total_transacoes else 0.0
    )

    clientes_ordenados = sorted(
        ((nome, round(total, 2)) for nome, total in por_cliente.items()),
        key=lambda item: (-item[1], item[0]),
    )

    resultado = {
        "total_transacoes": total_transacoes,
        "receita_total": float(receita_total),
        "ticket_medio": float(ticket_medio),
        "por_categoria": {
            cat: round(por_categoria[cat], 2) for cat in sorted(por_categoria)
        },
        "top_clientes": [
            {"cliente": nome, "total": total}
            for nome, total in clientes_ordenados[:top_n]
        ],
    }

    pasta = os.path.dirname(os.path.abspath(caminho_json_saida))
    os.makedirs(pasta, exist_ok=True)
    with open(caminho_json_saida, "w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    return resultado
