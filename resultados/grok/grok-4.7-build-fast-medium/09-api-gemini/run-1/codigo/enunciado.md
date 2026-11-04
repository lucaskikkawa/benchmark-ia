# 09 - Cliente Resiliente de API com Retry e Backoff

No diretório de trabalho, você encontrará o módulo `fake_api.py` que simula um servidor HTTP em processo através da classe `FakeApiServer`, sem exigir conexão real de rede.

Sua tarefa é implementar a classe `ClienteResiliente` e a exceção `ApiError` no arquivo `cliente_resiliente.py` na raiz do seu diretório de trabalho.

## Especificação de `cliente_resiliente.py`

### 1. Exceção `ApiError(Exception)`
- Deve herdar de `Exception`.
- Deve aceitar opcionalmente o atributo `status_code: int | None = None` e guardar a mensagem de erro.

### 2. Classe `ClienteResiliente`
- Construtor:
  ```python
  def __init__(
      self,
      servidor: FakeApiServer,
      max_tentativas: int = 3,
      backoff_base: float = 0.05,
      backoff_fator: float = 2.0,
      timeout: float = 2.0,
      sleep_fn: Callable[[float], None] = time.sleep,
  ) -> None:
      ...
  ```
  - **Validação de Parâmetros**:
    - Se `max_tentativas` não for um número inteiro (`type(max_tentativas) is int`) ou for `< 1`, deve levantar `ValueError`.
    - Se `backoff_base <= 0`, `backoff_fator <= 0` ou `timeout <= 0` (ou se forem de tipo não numérico / bool), deve levantar `ValueError`.
  - O parâmetro `sleep_fn` permite injetar uma função customizada de espera (como um mock de testes) para evitar pausas reais durante a suíte.

- Métodos:
  - `get(self, rota: str) -> dict`: atalho que invoca `self.executar("GET", rota)`.
  - `post(self, rota: str, payload: dict) -> dict`: atalho que invoca `self.executar("POST", rota, payload)`.
  - `executar(self, metodo: str, rota: str, payload: dict | None = None) -> dict`:
    - Chama `servidor.requisicao(metodo=metodo, rota=rota, payload=payload, timeout=self.timeout)`.
    - **Sucesso (status 2xx)**: retorna o dicionário `resposta.data`.
    - **Erros Retentáveis (Transitórios)**:
      - Exceções `SimulatedNetworkError` e `SimulatedTimeoutError`.
      - Respostas HTTP com status `429` (Rate Limit) e status `5xx` (`500`, `502`, `503`, `504`).
      - Caso ocorram, se a tentativa atual for menor que `max_tentativas`:
        - Calcula o tempo de espera através da fórmula de exponential backoff:
          `delay = backoff_base * (backoff_fator ** (tentativa - 1))`
        - Invoca `self.sleep_fn(delay)`.
        - Tenta novamente.
      - Se as tentativas se esgotarem (`tentativa == max_tentativas`), deve levantar `ApiError`. Se o esgotamento ocorreu devido a status HTTP retentável, o `ApiError` levantado deve ter `status_code` preenchido com o respectivo código HTTP retornado; se decorreu de erro de rede ou timeout, `status_code` deve ser `None`.
    - **Erros Não Retentáveis (Definitivos)**:
      - Qualquer resposta HTTP fora da faixa 2xx que não pertença ao conjunto de erros retentáveis (por exemplo `400`, `401`, `403`, `404`, ou códigos `3xx`).
      - Não deve tentar novamente; deve levantar imediatamente `ApiError` contendo o `status_code` correspondente.
