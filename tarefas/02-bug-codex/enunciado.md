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

Ambiente: Python 3.11, somente biblioteca padrão na solução; sem rede.
