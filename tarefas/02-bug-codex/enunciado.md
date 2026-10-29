# Corrigir somas de janelas

Edite `janelas.py`, já presente no diretório de trabalho. Preserve a assinatura:

```python
def somas_janelas(valores: list[int], tamanho: int) -> list[int]:
    ...
```

A função deve devolver a soma de CADA janela contígua de `tamanho` elementos,
na ordem original. Há `len(valores) - tamanho + 1` janelas quando o tamanho cabe.
O código inicial omite resultados em alguns casos. Corrija o bug preservando
os comportamentos válidos: tamanho maior que a lista devolve `[]`, tamanho zero
ou negativo lança `ValueError`, a lista recebida não muda. Os valores são inteiros
e `tamanho` é inteiro. Mantenha tempo O(n) para a varredura e nenhuma dependência.
Exemplo: `somas_janelas([1, 2, 3, 4], 2) == [3, 5, 7]`.

Os inteiros, inclusive as somas, podem ultrapassar 64 bits; mantenha resultados
exatos, sem conversão para float. Os testes incluem listas de até 200.000
valores com janelas grandes; O(n) vale também quando tamanho cresce com n.
Cada chamada deve produzir uma lista de resultados independente das anteriores.

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
