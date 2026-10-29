# Tarefa: cliente com retry, backoff e timeout para uma API simulada

O diretório de trabalho contém `fake_api.py` (**não altere**), uma API de usuários simulada em
processo, sem rede: `FakeAPI.requisitar(metodo, caminho, timeout) -> Resposta` pode devolver
respostas 500/503/429, levantar `ErroConexao` ou `TempoEsgotado` (quando a latência simulada
excede `timeout`), de forma determinística por `seed` ou por um `roteiro` de eventos. Leia o arquivo.

Crie `cliente.py` com:

```python
class ErroAPI(Exception): ...            # base dos erros do cliente
class NaoEncontrado(ErroAPI): ...        # recurso inexistente (404)
class FalhaPermanente(ErroAPI): ...      # tentativas esgotadas; atributo .tentativas: int

class ClienteAPI:
    def __init__(self, api, max_tentativas: int = 4, backoff_base: float = 0.5,
                 backoff_max: float = 8.0, timeout: float = 2.0, dormir=time.sleep): ...
    def obter_usuario(self, id_usuario: int) -> dict: ...
    def obter_varios(self, ids) -> dict[int, dict | None]: ...
```

`api` é qualquer objeto com `requisitar(metodo, caminho, timeout)` que retorna um objeto com
`.status`, `.corpo` e `.headers` (como `fake_api.Resposta`) ou levanta exceções.
`dormir` é a função usada para esperar entre tentativas (os testes injetam uma função falsa).

## Regras

- `__init__`: `ValueError` se `max_tentativas < 1`, `timeout <= 0`, `backoff_base < 0` ou `backoff_max < 0`.
- `obter_usuario(id)`: `ValueError` (sem nenhuma requisição) se `id` não for `int` (bool não vale) ou for `< 1`.
  Cada tentativa chama `api.requisitar("GET", f"/usuarios/{id}", timeout=self.timeout)`.
  - `200` → retorna `corpo`.
  - `404` → levanta `NaoEncontrado` imediatamente (sem retry).
  - Outros `4xx` exceto `429` → levanta `ErroAPI` imediatamente (sem retry).
  - **Retentáveis:** status `429`, `500`, `502`, `503`, `504` e as exceções `fake_api.ErroConexao` e
    `fake_api.TempoEsgotado`. Qualquer outra exceção da `api` propaga sem retry.
  - No máximo `max_tentativas` requisições no total. Antes da tentativa `n + 1` (após a falha `n`,
    com `n` começando em 1) chame `dormir(espera)` **uma vez**, com
    `espera = min(backoff_max, backoff_base * 2 ** (n - 1))`. Se a falha foi `429` com header
    `Retry-After` numérico (segundos, ex. `"2"` ou `"1.5"`), use `espera = min(backoff_max, float(Retry-After))`;
    se o header faltar ou não for numérico, use o backoff calculado.
  - Não chame `dormir` após a última tentativa nem antes da primeira.
  - Esgotadas as tentativas → `FalhaPermanente` com `.tentativas == max_tentativas`; se a última falha
    foi uma exceção, encadeie-a (`raise ... from erro`).
- `obter_varios(ids)`: retorna dict `id -> usuário` na ordem de primeira aparição; ids com `NaoEncontrado`
  mapeiam para `None`; ids repetidos são requisitados uma única vez; `FalhaPermanente` e `ValueError` propagam.

Use apenas a biblioteca padrão. Exemplo de uso:

```python
from fake_api import FakeAPI
from cliente import ClienteAPI
cliente = ClienteAPI(FakeAPI(seed=1, taxa_falha=0.4), max_tentativas=6, dormir=lambda s: None)
cliente.obter_usuario(7)   # {"id": 7, "nome": "Usuario 7"}
```
