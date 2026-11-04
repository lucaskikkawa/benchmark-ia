# Tarefa: horários livres em uma janela

Crie o arquivo `solucao.py` no diretório de trabalho com a função abaixo. Use apenas a biblioteca padrão do Python 3.11. Não crie outros arquivos.

```python
def horas_livres(
    ocupados: list[tuple[str, str]],
    inicio: str,
    fim: str,
) -> list[tuple[str, str]]:
    """Intervalos livres dentro da janela [inicio, fim)."""
```

## Horários

- Todo horário é uma string `HH:MM` com exatamente 5 caracteres, horas e minutos com dois dígitos ASCII (`0123456789`). O separador é o caractere `:` (U+003A).
- Minutos vão de `00` a `59`.
- Horas vão de `00` a `23`. O único valor extra aceito é `24:00` (fim do dia, equivalente a 1440 minutos). Na saída, 1440 minutos é `"24:00"`, nunca `"00:00"`.
- Qualquer outro texto é `ValueError`. Isso inclui `9:00`, `24:30`, `23:60`, `09-00`, `""`, `09:00:00`, `09:00 `, dígitos de largura cheia (`０９:００`), dois-pontos de largura cheia (`09：00`) e qualquer caractere que `str.isdigit` aceitaria mas não está em `0123456789`.
- Se um horário não for `str`, levante `TypeError`.

A janela e cada intervalo são semiabertos: o instante inicial entra e o final não entra. Na prática basta tratar os limites em minutos inteiros e devolver os trechos livres no mesmo formato.

## Janela

- `inicio` e `fim` formam a janela em que se busca disponibilidade.
- Exija `inicio` estritamente anterior a `fim`. Caso contrário, `ValueError`.
- `24:00` pode ser `fim`. Como início da janela ele nunca deixa a janela válida, então também é `ValueError`.

## Ocupados

- `ocupados` é exatamente uma `list`. `tuple`, `str`, gerador ou outro tipo: `TypeError`. Não itere uma string achando que cada caractere é um horário.
- Cada item é um `tuple` ou `list` de exatamente duas strings `(ini, fim)`. Forma errada: `TypeError`.
- Valide os dois horários e a ordem **antes** de ignorar ou recortar. Formato inválido ou `ini > fim` é erro mesmo que o intervalo caia fora da janela ou tenha duração zero (`("24:99", "24:99")` é `ValueError`, não é ignorado).
- `ini == fim` com horários válidos (duração zero): ignore esse item.
- Intervalos podem vir fora de ordem, sobrepostos, encostados, contidos uns nos outros, duplicados ou parcialmente fora da janela.
- Recorte cada ocupado para a janela. O que ficar inteiramente fora some.
- Una ocupados que se sobrepõem ou que se encostam (o fim de um é o início do outro), **depois do recorte**. Dois intervalos que só passam a se encostar dentro da janela também se unem. A união é transitiva.
- Não altere a lista recebida nem as listas internas que representam pares.

## Retorno

Lista de pares `(ini, fim)` em `HH:MM`, ordenada, sem sobreposição e sem duração zero, cobrindo exatamente o que sobrou da janela. `1440` minutos vira `"24:00"`. Se não houver folga, devolva `[]`.

## Exemplos

```python
horas_livres([], "09:00", "12:00")
# [("09:00", "12:00")]

horas_livres([("10:00", "11:00")], "09:00", "12:00")
# [("09:00", "10:00"), ("11:00", "12:00")]

horas_livres([("09:00", "10:00"), ("10:00", "11:00")], "09:00", "12:00")
# [("11:00", "12:00")]

horas_livres([("08:00", "09:30"), ("13:00", "15:00")], "09:00", "12:00")
# [("09:30", "12:00")]

horas_livres([("23:30", "24:00")], "23:00", "24:00")
# [("23:00", "23:30")]

horas_livres([("08:00", "11:00"), ("11:00", "13:00")], "10:00", "14:00")
# [("13:00", "14:00")]  recorte encosta 11:00 com 11:00 e funde
```
