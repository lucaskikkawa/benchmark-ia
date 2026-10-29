import csv
import json
import re
from pathlib import Path


def resumir_vendas(entrada, saida, minimo_centavos: int = 0) -> list[dict]:
    """Agregue vendas pagas e grave JSON somente após validar toda a entrada."""
    if type(minimo_centavos) is not int or minimo_centavos < 0:
        raise ValueError("mínimo negativo")
    totais = {}
    with open(entrada, encoding='utf-8-sig', newline='') as arquivo:
        leitor = csv.DictReader(arquivo)
        obrigatorias = {'produto', 'quantidade', 'preco_centavos', 'status'}
        if not obrigatorias.issubset(leitor.fieldnames or []):
            raise ValueError("colunas obrigatórias ausentes")
        for linha in leitor:
            if (linha['status'] or '').strip().lower() != 'pago':
                continue
            produto = (linha['produto'] or '').strip()
            numeros = [(linha[campo] or '').strip()
                       for campo in ('quantidade', 'preco_centavos')]
            if any(re.fullmatch(r'[+-]?[0-9]+', numero) is None for numero in numeros):
                raise ValueError("inteiro decimal ASCII inválido em venda paga")
            quantidade, preco = map(int, numeros)
            if not produto or quantidade < 0 or preco < 0:
                raise ValueError("venda paga inválida")
            total = totais.setdefault(produto, {'quantidade': 0, 'receita_centavos': 0})
            total['quantidade'] += quantidade
            total['receita_centavos'] += quantidade * preco
    resultado = [dict(produto=produto, **totais[produto]) for produto in sorted(totais)
                 if totais[produto]['receita_centavos'] >= minimo_centavos]
    Path(saida).write_text(json.dumps(resultado, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return resultado
