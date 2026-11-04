import csv
import json
import re
import sys

# Remove o limite de dígitos para conversão de inteiros em string no Python 3.11+
if hasattr(sys, "set_int_max_str_digits"):
    try:
        sys.set_int_max_str_digits(0)
    except Exception:
        pass

_NUM_PATTERN = re.compile(r"\A[+-]?[0-9]+\Z")


def _parse_int(val_str: str, field_name: str) -> int:
    s = val_str.strip()
    if not _NUM_PATTERN.match(s):
        raise ValueError(f"Valor numérico inválido para {field_name}: {val_str!r}")
    val = int(s)
    if val < 0:
        raise ValueError(f"Valor não pode ser negativo para {field_name}: {val}")
    return val


def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    # 1. Validação de minimo_centavos: deve ser exatamente int e >= 0
    if type(minimo_centavos) is not int or minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser exatamente um int >= 0")

    # 2. Leitura e validação do CSV de entrada
    totais: dict[str, list[int]] = {}

    with open(entrada, mode="r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f)

        first_row = next(reader, None)
        if first_row is None:
            raise ValueError("Arquivo vazio: cabeçalho ausente")

        col_map: dict[str, int] = {}
        for idx, col in enumerate(first_row):
            if col is not None:
                col_map[col] = idx
                col_map[col.strip()] = idx

        required_cols = ("produto", "quantidade", "preco_centavos", "status")
        for col in required_cols:
            if col not in col_map:
                raise ValueError(f"Coluna obrigatória ausente no cabeçalho: {col}")

        idx_prod = col_map["produto"]
        idx_qtd = col_map["quantidade"]
        idx_preco = col_map["preco_centavos"]
        idx_status = col_map["status"]

        for row in reader:
            # Linhas com campos faltando são ignoradas se não pagas
            if idx_status >= len(row):
                continue

            status = row[idx_status].strip().lower()
            if status != "pago":
                continue

            # Se pagas, campos obrigatórios faltantes são inválidos
            if idx_prod >= len(row) or idx_qtd >= len(row) or idx_preco >= len(row):
                raise ValueError("Campo obrigatório ausente em linha paga")

            prod = row[idx_prod].strip()
            if not prod:
                raise ValueError("Produto não pode ser vazio em linha paga")

            qtd = _parse_int(row[idx_qtd], "quantidade")
            preco = _parse_int(row[idx_preco], "preco_centavos")

            if prod not in totais:
                totais[prod] = [qtd, qtd * preco]
            else:
                totais[prod][0] += qtd
                totais[prod][1] += qtd * preco

    # 3. Filtragem por minimo_centavos após agregação
    resultado: list[dict] = []
    for prod, (qtd, receita) in totais.items():
        if receita >= minimo_centavos:
            resultado.append({
                "produto": prod,
                "quantidade": qtd,
                "receita_centavos": receita,
            })

    # 4. Ordenação padrão de strings Python por produto
    resultado.sort(key=lambda item: item["produto"])

    # 5. Gravação da saída em JSON UTF-8
    with open(saida, mode="w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False)
        f.write("\n")

    return resultado
