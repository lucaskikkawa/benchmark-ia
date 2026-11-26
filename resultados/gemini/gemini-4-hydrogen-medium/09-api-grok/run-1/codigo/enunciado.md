# Tarefa: cliente com retry, backoff e timeout

O arquivo `loja_api.py` já está no diretório de trabalho. É uma API **em processo**, sem socket e sem rede. Não altere `loja_api.py`. Crie `cliente.py` com:

```python
class TempoEsgotado(Exception):
    ...

def baixar_pedidos(
    api,
    ids: list[str],
    *,
    max_tentativas: int = 5,
    backoff_s: float = 0.0,
    timeout_s: float = 1.0,
) -> list[dict]:
    ...
```

Só a biblioteca padrão.

## O que a API faz

`LojaAPI(seed)` guarda a seed. `obter_pedido(pedido_id)` devolve o dict de `payload_pedido(seed, pedido_id)` ou levanta:

- `LojaErroCliente` — erro definitivo (o id começa com `missing-`, ou o id não é uma string não vazia, inclusive `""`). **Não tente de novo** e não durma backoff.
- `LojaIndisponivel` — falha transitória.

A lentidão é `LojaAPI.ATRASO_S` segundos (também exposto como `loja_api.ATRASO_S`). A contagem de tentativas começa em 1.

| prefixo do id | comportamento |
|---|---|
| `missing-` | sempre `LojaErroCliente` |
| `down-` | sempre `LojaIndisponivel` |
| `flaky-` | as primeiras `(seed % 3) + 1` tentativas são `LojaIndisponivel`; a próxima devolve o pedido |
| `slow-` | as primeiras `(seed % 2) + 1` tentativas dormem `ATRASO_S` e só então devolveriam o pedido |
| `timeout-` | toda tentativa dorme `ATRASO_S` e só então devolveria o pedido |
| outro | devolve o pedido na hora |

O prefixo é o começo do id, nesta ordem. `missing-down-x` é `LojaErroCliente`. `flaky-missing-x` segue a regra de `flaky-`, não a de `missing-`. O cliente não precisa reimplementar a tabela: chame `obter_pedido` e reaja à exceção.

`api.tentativas(pedido_id)` diz quantas vezes aquele id foi chamado. A seed entra no total do pedido; não invente o corpo, use o que a API devolver.

## O que o cliente faz

Para cada id, **na ordem da lista**:

1. Chame `api.obter_pedido(id)` com prazo de `timeout_s` segundos. Se a chamada passar disso, **abandone a espera** (não fique bloqueado os `ATRASO_S` segundos) e trate como timeout.
2. `LojaErroCliente` propaga na hora, sem nova tentativa e sem backoff.
3. `LojaIndisponivel` ou timeout contam como falha retentável.
4. Há no máximo `max_tentativas` chamadas daquele id. Se a última for `LojaIndisponivel`, propague essa exceção. Se a última for timeout, levante `TempoEsgotado`.
5. Depois de uma falha retentável que ainda terá outra tentativa, durma `backoff_s * 2 ** (i - 1)` segundos, onde `i` é o número da tentativa que acabou de falhar (1 na primeira). Não durma depois da última tentativa nem depois de sucesso. `backoff_s == 0` não dorme.
6. No sucesso, guarde o dict devolvido.

Se um id falha de vez (`LojaErroCliente`, `LojaIndisponivel` na última tentativa ou `TempoEsgotado`), não chame os ids seguintes. Lista vazia devolve `[]` sem chamar a API.

`slow-` com seed ímpar dorme nas duas primeiras tentativas (`(seed % 2) + 1 == 2`). Com `timeout_s` menor que `ATRASO_S`, essas duas contam como timeout e a terceira devolve o pedido, se `max_tentativas` alcançar.

Validação, antes de qualquer chamada:

- `ids` tem de ser exatamente `list` (`str` e `tuple` → `TypeError`). Não há cache: o mesmo id repetido na lista é baixado de novo e soma em `tentativas`.
- `max_tentativas` é `int` ≥ 1 (`bool` → `TypeError`; menor que 1 → `ValueError`).
- `backoff_s` é `int` ou `float` ≥ 0 (`bool` → `TypeError`; negativo → `ValueError`).
- `timeout_s` é `int` ou `float` > 0 (`bool` → `TypeError`; não positivo → `ValueError`).

O resultado conserva a ordem dos ids. Cada item é o dict da API (`id`, `total_centavos`, `status`).
