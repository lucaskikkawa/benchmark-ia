import csv
import json
import re
from pathlib import Path

_COLUNAS_OBRIGATORIAS = ("produto", "quantidade", "preco_centavos", "status")
_INTEIRO_ASCII_RE = re.compile(r"[+-]?[0-9]+", re.ASCII)


def _parse_inteiro_nao_negativo(valor: str, campo: str) -> int:
    texto = valor.strip()
    if _INTEIRO_ASCII_RE.fullmatch(texto) is None:
        raise ValueError(f"Valor inválido para {campo!r}: {valor!r}")
    numero = int(texto)
    if numero < 0:
        raise ValueError(f"Valor negativo para {campo!r}: {valor!r}")
    return numero


def resumir_vendas(
    entrada: str | Path,
    saida: str | Path,
    minimo_centavos: int = 0,
) -> list[dict]:
    if type(minimo_centavos) is not int or minimo_centavos < 0:
        raise ValueError("minimo_centavos deve ser um inteiro (int) >= 0.")

    acumulado: dict[str, list[int]] = {}

    with open(entrada, "r", encoding="utf-8-sig", newline="") as arquivo_entrada:
        leitor = csv.reader(arquivo_entrada)
        cabecalho = next(leitor, None)
        if cabecalho is None:
            raise ValueError("Arquivo CSV vazio: cabeçalho obrigatório ausente.")

        indices = {nome: idx for idx, nome in enumerate(cabecalho)}
        for coluna in _COLUNAS_OBRIGATORIAS:
            if coluna not in indices:
                raise ValueError(f"Coluna obrigatória ausente no cabeçalho: {coluna!r}")

        idx_produto = indices["produto"]
        idx_quantidade = indices["quantidade"]
        idx_preco = indices["preco_centavos"]
        idx_status = indices["status"]
        max_idx_obrigatorio = max(idx_produto, idx_quantidade, idx_preco, idx_status)

        for linha in leitor:
            if len(linha) <= idx_status:
                continue
            if linha[idx_status].strip().lower() != "pago":
                continue

            if len(linha) <= max_idx_obrigatorio:
                raise ValueError("Linha paga com campos obrigatórios faltando.")

            produto = linha[idx_produto].strip()
            if not produto:
                raise ValueError("Produto vazio em linha paga.")

            quantidade = _parse_inteiro_nao_negativo(linha[idx_quantidade], "quantidade")
            preco_centavos = _parse_inteiro_nao_negativo(
                linha[idx_preco], "preco_centavos"
            )

            totais = acumulado.get(produto)
            if totais is None:
                acumulado[produto] = [quantidade, quantidade * preco_centavos]
            else:
                totais[0] += quantidade
                totais[1] += quantidade * preco_centavos

    resultado = [
        {
            "produto": produto,
            "quantidade": totais[0],
            "receita_centavos": totais[1],
        }
        for produto, totais in sorted(
            (item for item in acumulado.items() if item[1][1] >= minimo_centavos),
            key=lambda item: item[0],
        )
    ]

    conteudo_json = json.dumps(resultado, ensure_ascii=False, indent=2) + "\n"
    with open(saida, "w", encoding="utf-8", newline="\n") as arquivo_saida:
        arquivo_saida.write(conteudo_json)

    return resultado
