# Tarefa: corrigir o fechamento de boletim

O arquivo `boletim.py` (no diretório de trabalho) expõe `fechar_boletim(provas)`. O comportamento abaixo é o contrato. A implementação atual discorda dele em vários pontos (notas de fronteira, ausências, descarte, arredondamento, conceitos e a própria lista recebida). **Edite apenas `boletim.py`**. Não mude o nome nem a assinatura. Use só a biblioteca padrão.

```python
def fechar_boletim(provas: list) -> dict:
    ...
```

## Entrada

`provas` é uma `list` com 1 a 4 posições. Cada item é:

- `int` ou `float` finito no intervalo fechado `[0, 10]`, ou
- `None`, que significa ausência e **não entra** na conta (não é zero).

`bool` não é nota (`True`/`False` → `TypeError`). Outro tipo que não seja `int`, `float` ou `None` → `TypeError`. `provas` que não seja `list` → `TypeError`.

`ValueError` quando:

- `len(provas)` é 0 ou maior que 4;
- depois de ignorar `None` não sobra nenhuma nota;
- alguma nota não é finita ou está fora de `[0, 10]` (10 e 0 são válidos).

Não altere a lista recebida.

## Cálculo

1. Separe as notas válidas, na ordem original, ignorando `None`.
2. Só quando houver **exatamente 4** notas válidas, descarte **uma** ocorrência do menor valor (se houver empate, remova só a primeira). Com 1, 2 ou 3 notas válidas não se descarta nada. O campo `descartada` é esse valor convertido com `float`, ou `None` se nada foi descartado.
3. Converta cada nota restante com `Decimal(str(nota))` (não use `Decimal(nota)` direto num float). A média é `(soma / n).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)` e o campo `media` é `float` desse resultado.
4. Conceito em cima da média já arredondada, limites inclusivos:
   - `>= 9` → `"A"`
   - `>= 7` → `"B"`
   - `>= 5` → `"C"`
   - caso contrário → `"D"`
5. `aprovado` é `True` somente quando o conceito não é `"D"`.

## Retorno

Dict com exatamente estas chaves:

```python
{
    "media": float,
    "conceito": str,       # "A", "B", "C" ou "D"
    "aprovado": bool,
    "descartada": float | None,
}
```

## Exemplos

```python
fechar_boletim([9])                # media 9.0,  conceito "A", aprovado True,  descartada None
fechar_boletim([7])                # media 7.0,  conceito "B"
fechar_boletim([5])                # media 5.0,  conceito "C"
fechar_boletim([4])                # media 4.0,  conceito "D", aprovado False
fechar_boletim([1.005])            # media 1.01
fechar_boletim([4.999])            # media 5.0,  conceito "C"
fechar_boletim([1.0, 1.01])        # media 1.01, descartada None
fechar_boletim([1, 2, 3, 4])       # descarta 1.0, media 3.0, conceito "D"
fechar_boletim([10, 0, 10, 10])    # descarta 0.0, media 10.0, conceito "A"
fechar_boletim([None, 8, 8])       # media 8.0, descartada None
fechar_boletim([])                  # ValueError
fechar_boletim([None, None])        # ValueError
fechar_boletim([1, 1, 1, 1, 1])     # ValueError
fechar_boletim([True])              # TypeError
```
