"""Processamento de vendas a partir de um arquivo CSV."""

import csv
import json
import math
from pathlib import Path


def processar_vendas(
    caminho_csv: str,
    caminho_json_saida: str,
    status_filtro: str = "concluido",
    top_n: int = 3,
) -> dict:
    """Agrega as vendas válidas do CSV e grava o resultado em JSON."""
    if type(top_n) is not int:
        raise TypeError("top_n deve ser um inteiro")
    if top_n < 1:
        raise ValueError("top_n deve ser maior ou igual a 1")

    arquivo_csv = Path(caminho_csv)
    if not arquivo_csv.is_file():
        raise FileNotFoundError(caminho_csv)

    total_transacoes = 0
    receita = 0.0
    categorias = {}
    clientes = {}

    # utf-8-sig remove um BOM inicial; newline vazio deixa o módulo csv
    # tratar corretamente as terminações de linha.
    with arquivo_csv.open("r", encoding="utf-8-sig", newline="") as arquivo:
        leitor = csv.DictReader(arquivo)
        if leitor.fieldnames is not None:
            leitor.fieldnames = [
                nome.strip() if nome is not None else ""
                for nome in leitor.fieldnames
            ]
            status_esperado = str(status_filtro).strip().casefold()

            for linha in leitor:
                if not linha or all(
                    valor is None or str(valor).strip() == ""
                    for valor in linha.values()
                ):
                    continue

                status = linha.get("status")
                if status is None or status.strip().casefold() != status_esperado:
                    continue

                valor_texto = linha.get("valor")
                if valor_texto is None:
                    continue
                try:
                    valor = float(valor_texto.strip())
                except (TypeError, ValueError):
                    continue
                if not math.isfinite(valor) or valor < 0:
                    continue

                cliente = (linha.get("cliente") or "").strip()
                categoria = (linha.get("categoria") or "").strip()

                total_transacoes += 1
                receita += valor
                categorias[categoria] = categorias.get(categoria, 0.0) + valor
                clientes[cliente] = clientes.get(cliente, 0.0) + valor

    receita_total = round(receita, 2)
    ticket_medio = (
        round(receita_total / total_transacoes, 2) if total_transacoes else 0.0
    )
    totais_clientes = [
        {"cliente": cliente, "total": round(total, 2)}
        for cliente, total in clientes.items()
    ]
    totais_clientes.sort(key=lambda item: (-item["total"], item["cliente"]))

    resultado = {
        "total_transacoes": total_transacoes,
        "receita_total": receita_total,
        "ticket_medio": ticket_medio,
        "por_categoria": {
            categoria: round(categorias[categoria], 2)
            for categoria in sorted(categorias)
        },
        "top_clientes": totais_clientes[:top_n],
    }

    caminho_saida = Path(caminho_json_saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open("w", encoding="utf-8") as arquivo:
        json.dump(resultado, arquivo, indent=2, ensure_ascii=False)

    return resultado
