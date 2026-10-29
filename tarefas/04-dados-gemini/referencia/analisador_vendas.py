import csv
import json
from collections import defaultdict
from pathlib import Path


def processar_vendas(
    caminho_csv: str,
    caminho_json_saida: str,
    status_filtro: str = "concluido",
    top_n: int = 3,
) -> dict:
    """Lê transações de um arquivo CSV, filtra, agrega métricas e salva em JSON."""
    if top_n < 1:
        raise ValueError("O parâmetro top_n deve ser pelo menos 1.")

    p_csv = Path(caminho_csv)
    if not p_csv.is_file():
        raise FileNotFoundError(f"Arquivo CSV não encontrado: {caminho_csv}")

    status_filtro_norm = status_filtro.strip().lower()

    transacoes_filtradas = []
    por_categoria = defaultdict(float)
    por_cliente = defaultdict(float)

    with open(p_csv, mode="r", encoding="utf-8") as f:
        leitor = csv.DictReader(f)
        for linha in leitor:
            if not linha:
                continue
            status_linha = (linha.get("status") or "").strip().lower()
            if status_linha != status_filtro_norm:
                continue

            try:
                valor_raw = (linha.get("valor") or "").strip()
                valor = float(valor_raw)
                if valor < 0:
                    continue
            except (ValueError, TypeError):
                continue

            cliente = (linha.get("cliente") or "").strip()
            categoria = (linha.get("categoria") or "").strip()

            transacoes_filtradas.append(valor)
            por_categoria[categoria] += valor
            por_cliente[cliente] += valor

    total_transacoes = len(transacoes_filtradas)
    receita_total = round(sum(transacoes_filtradas), 2)
    ticket_medio = round(receita_total / total_transacoes, 2) if total_transacoes > 0 else 0.0

    dict_categorias = {
        cat: round(val, 2)
        for cat, val in sorted(por_categoria.items(), key=lambda x: x[0])
    }

    # Ordena clientes por valor decrescente e nome alfabético crescente
    clientes_ordenados = sorted(
        por_cliente.items(),
        key=lambda item: (-item[1], item[0]),
    )
    top_clientes = [
        {"cliente": nome, "total": round(val, 2)}
        for nome, val in clientes_ordenados[:top_n]
    ]

    resultado = {
        "total_transacoes": total_transacoes,
        "receita_total": receita_total,
        "ticket_medio": ticket_medio,
        "por_categoria": dict_categorias,
        "top_clientes": top_clientes,
    }

    p_saida = Path(caminho_json_saida)
    p_saida.parent.mkdir(parents=True, exist_ok=True)
    with open(p_saida, mode="w", encoding="utf-8") as f:
        json.dump(resultado, f, indent=2, ensure_ascii=False)

    return resultado
