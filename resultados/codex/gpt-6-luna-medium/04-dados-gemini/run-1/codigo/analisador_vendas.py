"""Processamento de vendas a partir de um CSV."""

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
    """Agrega vendas válidas do CSV e grava o resultado em JSON.

    Apenas transações com status correspondente a ``status_filtro`` são
    consideradas. Valores inválidos, negativos ou não finitos são ignorados.
    """
    if type(top_n) is not int:
        raise TypeError("top_n deve ser um inteiro")
    if top_n < 1:
        raise ValueError("top_n deve ser maior ou igual a 1")

    arquivo_csv = Path(caminho_csv)
    if not arquivo_csv.is_file():
        raise FileNotFoundError(caminho_csv)

    total_transacoes = 0
    receita_bruta = 0.0
    categorias = {}
    clientes = {}

    # Um arquivo de zero bytes não contém nem cabeçalho; tratá-lo como vazio
    # evita que DictReader levante StopIteration.
    if arquivo_csv.stat().st_size > 0:
        with arquivo_csv.open("r", encoding="utf-8-sig", newline="") as arquivo:
            leitor = csv.DictReader(arquivo, skipinitialspace=False)
            if leitor.fieldnames:
                leitor.fieldnames = [
                    nome.strip() if nome is not None else ""
                    for nome in leitor.fieldnames
                ]

            filtro_normalizado = status_filtro.strip().casefold()
            for linha in leitor:
                if not linha or all(valor is None or not valor.strip() for valor in linha.values()):
                    continue

                status = linha.get("status")
                if status is None or status.strip().casefold() != filtro_normalizado:
                    continue

                texto_valor = linha.get("valor")
                if texto_valor is None:
                    continue
                try:
                    valor = float(texto_valor.strip())
                except (TypeError, ValueError):
                    continue
                if not math.isfinite(valor) or valor < 0:
                    continue

                cliente = (linha.get("cliente") or "").strip()
                categoria = (linha.get("categoria") or "").strip()

                total_transacoes += 1
                receita_bruta += valor
                categorias[categoria] = categorias.get(categoria, 0.0) + valor
                clientes[cliente] = clientes.get(cliente, 0.0) + valor

    receita_total = round(receita_bruta, 2)
    ticket_medio = (
        round(receita_total / total_transacoes, 2) if total_transacoes else 0.0
    )
    por_categoria = {
        nome: round(total, 2)
        for nome, total in sorted(categorias.items(), key=lambda item: item[0])
    }

    # O desempate e o corte consideram os totais dos clientes já arredondados,
    # conforme a especificação.
    clientes_arredondados = [
        {"cliente": nome, "total": round(total, 2)}
        for nome, total in clientes.items()
    ]
    clientes_arredondados.sort(key=lambda item: (-item["total"], item["cliente"]))

    resultado = {
        "total_transacoes": total_transacoes,
        "receita_total": receita_total,
        "ticket_medio": ticket_medio,
        "por_categoria": por_categoria,
        "top_clientes": clientes_arredondados[:top_n],
    }

    arquivo_saida = Path(caminho_json_saida)
    arquivo_saida.parent.mkdir(parents=True, exist_ok=True)
    with arquivo_saida.open("w", encoding="utf-8") as arquivo:
        json.dump(resultado, arquivo, indent=2, ensure_ascii=False)

    return resultado
