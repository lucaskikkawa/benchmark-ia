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

- Todo horário é uma string `HH:MM` com exatamente 5 caracteres, horas e minutos com dois dígitos.
- Minutos vão de `00` a `59`.
- Horas vão de `00` a `23`. O único valor extra aceito é `24:00` (fim do dia, equivalente a 1440 minutos).
- Qualquer outro texto (`9:00`, `24:30`, `23:60`, `09-00`, `""`, `09:00:00`) é inválido e deve levantar `ValueError`.
- Se um horário não for `str`, levante `TypeError`.

A janela e cada intervalo são semiabertos: o instante inicial entra e o final não entra. Na prática basta tratar os limites em minutos inteiros e devolver os trechos livres no mesmo formato.

## Janela

- `inicio` e `fim` formam a janela em que se busca disponibilidade.
- Exija `inicio` estritamente anterior a `fim`. Caso contrário, `ValueError`.
- `24:00` pode ser `fim`. Como início da janela ele nunca deixa a janela válida, então também é `ValueError`.

## Ocupados

- `ocupados` é uma lista (não aceita `str` nem outro tipo não iterável: `TypeError`).
- Cada item é um `tuple` ou `list` de exatamente duas strings `(ini, fim)`. Forma errada: `TypeError`.
- `ini > fim` no intervalo ocupado: `ValueError`.
- `ini == fim` (duração zero): ignore esse item.
- Intervalos podem vir fora de ordem, sobrepostos, encostados, contidos uns nos outros ou parcialmente fora da janela.
- Recorte cada ocupado para a janela. O que ficar inteiramente fora some.
- Una ocupados que se sobrepõem ou que se encostam (o fim de um é o início do outro).
- Não altere a lista recebida.

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
```
