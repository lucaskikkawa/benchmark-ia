import time
from typing import Callable
from fake_api import (
    ApiResponse,
    FakeApiServer,
    SimulatedNetworkError,
    SimulatedTimeoutError,
)


class ApiError(Exception):
    """Exceção levantada quando uma requisição falha definitivamente."""

    def __init__(self, message: str, status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.status_code = status_code


class ClienteResiliente:
    """Cliente HTTP com suporte a retry, exponential backoff e timeout."""

    STATUS_RETENTAVEIS = {429, 500, 502, 503, 504}

    def __init__(
        self,
        servidor: FakeApiServer,
        max_tentativas: int = 3,
        backoff_base: float = 0.05,
        backoff_fator: float = 2.0,
        timeout: float = 2.0,
        sleep_fn: Callable[[float], None] = time.sleep,
    ) -> None:
        if type(max_tentativas) is not int or max_tentativas < 1:
            raise ValueError("max_tentativas deve ser um inteiro maior ou igual a 1.")

        for nome_param, val in [("backoff_base", backoff_base), ("backoff_fator", backoff_fator), ("timeout", timeout)]:
            if type(val) is bool or type(val) not in (int, float) or val <= 0:
                raise ValueError(f"{nome_param} deve ser numérico maior que zero.")

        self.servidor = servidor
        self.max_tentativas = max_tentativas
        self.backoff_base = float(backoff_base)
        self.backoff_fator = float(backoff_fator)
        self.timeout = float(timeout)
        self.sleep_fn = sleep_fn

    def get(self, rota: str) -> dict:
        return self.executar("GET", rota)

    def post(self, rota: str, payload: dict) -> dict:
        return self.executar("POST", rota, payload)

    def executar(self, metodo: str, rota: str, payload: dict | None = None) -> dict:
        for tentativa in range(1, self.max_tentativas + 1):
            try:
                resposta: ApiResponse = self.servidor.requisicao(
                    metodo=metodo,
                    rota=rota,
                    payload=payload,
                    timeout=self.timeout,
                )

                # Sucesso 2xx
                if 200 <= resposta.status_code < 300:
                    return resposta.data

                # Falhas de servidor ou rate limit que justificam retry
                if resposta.status_code in self.STATUS_RETENTAVEIS:
                    if tentativa < self.max_tentativas:
                        delay = self.backoff_base * (self.backoff_fator ** (tentativa - 1))
                        self.sleep_fn(delay)
                        continue
                    raise ApiError(
                        f"Falha na API com status {resposta.status_code}: {resposta.data}",
                        status_code=resposta.status_code,
                    )

                # Erros não recuperáveis (4xx exceto 429, 3xx, etc.) -> falha imediata sem retry
                raise ApiError(
                    f"Erro de requisição com status {resposta.status_code}: {resposta.data}",
                    status_code=resposta.status_code,
                )

            except (SimulatedNetworkError, SimulatedTimeoutError) as exc:
                if tentativa < self.max_tentativas:
                    delay = self.backoff_base * (self.backoff_fator ** (tentativa - 1))
                    self.sleep_fn(delay)
                    continue

                raise ApiError(
                    f"Tentativas esgotadas ({self.max_tentativas}) devido a erro de rede/timeout: {exc}",
                    status_code=None,
                ) from exc

        raise ApiError("Tentativas esgotadas sem resposta válida.", status_code=None)
