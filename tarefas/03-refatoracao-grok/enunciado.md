# Tarefa: refatorar a cotação de frete

O arquivo `frete.py` calcula o frete certo, mas a tabela está copiada em ramos e não há onde reutilizá-la. **Refatore `frete.py`** sem mudar o resultado de `cotar` para nenhuma entrada válida ou inválida.

Mantenha a função:

```python
def cotar(peso_g: int, distancia_km: int, expresso: bool) -> dict:
    ...
```

E passe a expor também:

```python
class TabelaFrete:
    FAIXAS: tuple[tuple[str, int, int, int, int], ...]

    def cotar(self, peso_g: int, distancia_km: int, expresso: bool) -> dict:
        """Mesmo contrato da função cotar."""

def faixa_de_peso(peso_g: int) -> str:
    """Nome da faixa. Mesmas regras de tipo e intervalo de cotar para o peso."""
```

`TabelaFrete` não recebe argumentos no construtor. `FAIXAS` é atributo de classe. A função `cotar` deve produzir o mesmo dict que `TabelaFrete().cotar(...)`.

`FAIXAS` é uma sequência de tuplas `(nome, peso_min, peso_max, base_centavos, centavos_por_km)`, limites de peso inclusivos, exatamente nesta ordem e com estes números:

| nome | peso_min | peso_max | base_centavos | centavos_por_km |
|---|---:|---:|---:|---:|
| carta | 1 | 300 | 800 | 0 |
| pac | 301 | 2000 | 1500 | 2 |
| sedex | 2001 | 10000 | 2500 | 5 |
| transportadora | 10001 | 30000 | 4000 | 8 |

## Comportamento (não mude)

- `peso_g` e `distancia_km` são `int`. `bool` não vale: `TypeError`.
- `expresso` é `bool`. Outro tipo: `TypeError`.
- `peso_g` fora de `1..30000`: `ValueError`.
- `distancia_km` fora de `0..3000`: `ValueError`.
- `valor = base_centavos + centavos_por_km * distancia_km`.
- Se `expresso` for `True`, `valor = (valor * 3) // 2` (divisão inteira, sem float).
- Retorno exatamente:

```python
{"faixa": nome, "valor_centavos": valor, "expresso": expresso}
```

`faixa_de_peso` só olha o peso: devolve o nome da faixa ou levanta o mesmo `TypeError`/`ValueError` de peso inválido. Não peça distância.

Exemplos:

```python
cotar(300, 100, False)   # {"faixa": "carta", "valor_centavos": 800, "expresso": False}
cotar(301, 1, True)      # {"faixa": "pac", "valor_centavos": 2253, "expresso": True}
cotar(10001, 1, False)   # {"faixa": "transportadora", "valor_centavos": 4008, "expresso": False}
faixa_de_peso(2001)      # "sedex"
```

`2253` vem de `1500 + 2 * 1 = 1502` e `(1502 * 3) // 2`.

Use apenas a biblioteca padrão. Não crie outros módulos.
