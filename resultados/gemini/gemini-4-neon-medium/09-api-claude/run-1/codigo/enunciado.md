# Tarefa: cliente com retry, backoff e timeout para uma API simulada

O diretório de trabalho contém `fake_api.py` (**não altere**), uma API de usuários simulada em
processo, sem rede: `FakeAPI.requisitar(metodo, caminho, timeout) -> Resposta` pode devolver
respostas 500/503/429, levantar `ErroConexao` ou `TempoEsgotado` (quando a latência simulada
excede `timeout`), de forma determinística por `seed` ou por um `roteiro` de eventos. Leia o arquivo.

Crie `cliente.py` com:

```python
class ErroAPI(Exception): ...            # base dos erros do cliente
class NaoEncontrado(ErroAPI): ...        # recurso inexistente (404)
class FalhaPermanente(ErroAPI): ...      # desistiu; atributo .tentativas: int

class ClienteAPI:
    def __init__(self, api, max_tentativas: int = 4, backoff_base: float = 0.5,
                 backoff_max: float = 8.0, timeout: float = 2.0, dormir=time.sleep,
                 orcamento_espera: float | None = None): ...
    def obter_usuario(self, id_usuario: int) -> dict: ...
    def obter_varios(self, ids) -> dict[int, dict | None]: ...
```

`api` é qualquer objeto com `requisitar(metodo, caminho, timeout)` que retorna um objeto com
`.status`, `.corpo` e `.headers` (como `fake_api.Resposta`) ou levanta exceções.
`dormir` é a função usada para esperar entre tentativas (os testes injetam uma função falsa).

## Regras

- `__init__`: `ValueError` se `max_tentativas < 1`, `timeout <= 0`, `backoff_base < 0`, `backoff_max < 0`
  ou `orcamento_espera < 0`. `max_tentativas` pode ser grande (ex.: `2000`).
- `obter_usuario(id)`: `ValueError` (sem nenhuma requisição) se `id` não for `int` (bool não vale) ou for `< 1`.
  Cada tentativa chama `api.requisitar("GET", f"/usuarios/{id}", timeout=self.timeout)`.
  - `200` → retorna `corpo`.
  - `404` → levanta `NaoEncontrado` imediatamente (sem retry).
  - Qualquer outro status que não seja `200`, `404` nem retentável (ex.: `400`, `403`, `301`, `501`)
    → levanta `ErroAPI` imediatamente (sem retry).
  - Os `ErroAPI` levantados por causa de um status HTTP (inclusive `NaoEncontrado`) têm o atributo
    `.status` com o código recebido.
  - **Retentáveis:** status `429`, `500`, `502`, `503`, `504` e as exceções `fake_api.ErroConexao` e
    `fake_api.TempoEsgotado`. Qualquer outra exceção da `api` propaga sem retry.
  - No máximo `max_tentativas` requisições no total. Antes da tentativa `n + 1` (após a falha `n`,
    com `n` começando em 1) chame `dormir(espera)` **uma vez**, com
    `espera = min(backoff_max, backoff_base * 2 ** (n - 1))` (calculada sem estourar, mesmo com `n` na
    casa dos milhares). Se a falha foi `429` com header `Retry-After` numérico (segundos, ex. `"2"` ou
    `"1.5"`; o nome do header não diferencia maiúsculas/minúsculas, ex. `retry-after`), use
    `espera = min(backoff_max, float(Retry-After))`; se o header faltar, não for numérico ou não for um
    número finito `>= 0` (ex. `"-1"`, `"nan"`, `"inf"`), use o backoff calculado.
  - Não chame `dormir` após a última tentativa nem antes da primeira.
  - **Orçamento:** se `orcamento_espera` não for `None` e a próxima espera fizer a soma das esperas desta
    chamada de `obter_usuario` passar de `orcamento_espera` (estritamente maior), **não** espere: desista na
    hora com `FalhaPermanente`.
  - Esgotadas as tentativas (ou o orçamento) → `FalhaPermanente` com `.tentativas` = número de requisições
    feitas nesta chamada; se a última falha foi uma exceção, encadeie-a (`raise ... from erro`); se foi
    um status HTTP, `__cause__` deve ser `None`.
- `obter_varios(ids)`: `ids` é qualquer iterável (inclusive gerador). Valida **todos** os ids antes de
  qualquer requisição (um id inválido → `ValueError` sem nenhuma requisição). Retorna dict `id -> usuário`
  na ordem de primeira aparição; ids com `NaoEncontrado` mapeiam para `None`; ids repetidos são
  requisitados uma única vez; `FalhaPermanente` e outros `ErroAPI` propagam.

Use apenas a biblioteca padrão. Exemplo de uso:

```python
from fake_api import FakeAPI
from cliente import ClienteAPI
cliente = ClienteAPI(FakeAPI(seed=1, taxa_falha=0.4), max_tentativas=6, dormir=lambda s: None)
cliente.obter_usuario(7)   # {"id": 7, "nome": "Usuario 7"}
```
